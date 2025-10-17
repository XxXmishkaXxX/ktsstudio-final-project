import typing

from rmq_core.rmq import RabbitMQ

from app.rmq.rmq_callback import rmq_callback

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_rabbitmq(app: "Application"):
    app.rmq = RabbitMQ(app)

    async def start(_app):
        try:
            await app.rmq.connect()
            await app.rmq.consume(rmq_callback)
        except Exception as e:
            app.logger.error(str(e))

    async def close(_app):
        await app.rmq.close()

    app.on_startup.append(start)
    app.on_cleanup.append(close)
