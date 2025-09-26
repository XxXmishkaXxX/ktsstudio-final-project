from typing import TYPE_CHECKING
from aiohttp import web

from app.bot.routes import routes 


if TYPE_CHECKING:
    from app.web.app import Application



def setup_routes(app: "Application"):
    app.add_routes(routes)

    app.router.add_get("/health", lambda request: web.Response(text="ok"))

