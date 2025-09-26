from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):

    app.router.add_get(
        "/health", lambda request: web.json_response({"status": "ok"})
    )
