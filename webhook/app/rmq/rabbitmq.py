import typing

import aio_pika

if typing.TYPE_CHECKING:
    from app.web.app import Application


class RabbitMQ:
    def __init__(
        self, host: str, port: int, user: str, password: str, queue: str
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.queue_name = queue

        self._connection = None
        self._channel = None
        self.queue = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.user,
            password=self.password,
        )
        self._channel = await self._connection.channel()

        self.queue = await self._channel.declare_queue(
            self.queue_name, durable=True
        )

    async def publish(self, message: str):
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=self.queue_name,
        )

    async def close(self):
        if self._connection:
            await self._connection.close()


def setup_rabbitmq(app: "Application"):
    rmq_conf = app.config.rmq
    app.rmq = RabbitMQ(
        host=rmq_conf.host,
        port=rmq_conf.port,
        user=rmq_conf.user,
        password=rmq_conf.password,
        queue=rmq_conf.queue,
    )

    async def start(_app):
        try:
            await app.rmq.connect()
        except Exception as e:
            app.logger.error(str(e))

    async def close(_app):
        await app.rmq.close()

    app.on_startup.append(start)
    app.on_cleanup.append(close)
