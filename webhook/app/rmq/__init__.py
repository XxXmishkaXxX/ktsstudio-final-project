import typing

from rmq_core.rmq import RabbitMQ

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_rabbitmq(app: "Application"):
    app.rmq = RabbitMQ(app)

    async def start(_app):
        try:
            await app.rmq.connect()
        except Exception as e:
            app.logger.error(str(e))

    async def close(_app):
        await app.rmq.close()

    app.on_startup.append(start)
    app.on_cleanup.append(close)
