from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
)
from db_core.database.db import Database
from tg_client.client import TelegramBot
from tg_client.setup import setup_telegram_client

from app.recovery.setup import HeartbeatService, RecoveryService, setup_recovery
from app.rmq import RabbitMQ, setup_rabbitmq
from app.services.setup import (
    GameRenderer,
    GameService,
    RoundService,
    TimerService,
    setup_services,
)
from app.store import Store, setup_store
from app.store.cache.cache import Cache
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
    heartbeat: HeartbeatService
    recovery: RecoveryService


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_store(app)
    setup_services(app)
    setup_telegram_client(app)
    setup_routes(app)
    setup_rabbitmq(app)
    setup_recovery(app)

    return app
