from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
)
from app.bot.client import TelegramBot, setup_telegram_client
from app.games.services.setup import (
    setup_services,
    GameRenderer,
    GameService,
    RoundService,
    TimerService,
)
from app.rmq.rabbitmq import RabbitMQ, setup_rabbitmq
from app.store import Store, setup_store
from app.store.cache.cache import Cache
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config
    database: Database
    cache: Cache
    store: Store
    telegram: TelegramBot
    rmq: RabbitMQ
    timer_service: TimerService
    renderer: GameRenderer
    round_service: RoundService
    game_service: GameService


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()


def setup_app(config_path: str) -> Application:
    app = Application()
    setup_logging(app)
    setup_config(app, config_path)
    setup_store(app)
    setup_services(app)
    setup_telegram_client(app)
    setup_routes(app)
    setup_rabbitmq(app)

    return app
