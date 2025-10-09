from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from db_core.models.admins import AdminModel
from app.store import Store, setup_store
from db_core.database.db import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config
    database: Database
    store: Store


class Request(AiohttpRequest):
    admin: AdminModel | None = None


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self) -> Database:
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_store(app)
    session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_middlewares(app)
    setup_aiohttp_apispec(
        app=app,
        title="My API",
        version="v1",
    )
    setup_routes(app)
    return app
