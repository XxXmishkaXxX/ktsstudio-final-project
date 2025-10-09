from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
)
from app.bot.webhook import TelegramBot, setup_webhook
from app.rmq.rabbitmq import RabbitMQ, setup_rabbitmq
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config
    bot: TelegramBot
    rmq: RabbitMQ


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_webhook(app)
    setup_rabbitmq(app)
    setup_routes(app)

    return app
