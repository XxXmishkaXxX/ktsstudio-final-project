import functools
import typing

import aio_pika


class RabbitMQ:
    def __init__(self, app):
        self.app = app

        self._connection = None
        self._channel = None
        self.queue = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(
            host=self.app.config.rmq.host,
            port=self.app.config.rmq.port,
            login=self.app.config.rmq.user,
            password=self.app.config.rmq.password,
        )
        self._channel = await self._connection.channel()

        self.queue = await self._channel.declare_queue(
            self.app.config.rmq.queue, durable=True
        )

    async def consume(
        self,
        callback: typing.Callable[[aio_pika.IncomingMessage], typing.Coroutine],
    ):
        if not self.queue:
            raise RuntimeError("Queue is not declared. Call connect() first.")

        wrapped_callback = functools.partial(callback, app=self.app)

        await self.queue.consume(wrapped_callback, no_ack=False)

    async def publish(self, message: str, retry: int = 3) -> None:
        for _ in range(retry):
            try:
                await self._channel.default_exchange.publish(
                    aio_pika.Message(body=message.encode()),
                    routing_key=self.queue.name,
                )
                return  # noqa: RUF001 досрочный выход допустим
            except aio_pika.exceptions.AMQPConnectionError:
                await self.connect()
        raise RuntimeError("Failed to publish message after retries")

    async def close(self):
        if self._connection:
            await self._connection.close()
