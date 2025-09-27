from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from app.admin.models import AdminModel
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.routes import setup_routes
from app.web.middlewares import setup_middlewares
from aiohttp_apispec import setup_aiohttp_apispec


class Application(AiohttpApplication):
    config: Config
    database: Database
    store: Store


class Request(AiohttpRequest):
    admin: AdminModel | None = None

    @property
    def app(self) -> Application:
        return super().app()


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


def setup_app(config_path: str) -> Application:
    app = Application()
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
