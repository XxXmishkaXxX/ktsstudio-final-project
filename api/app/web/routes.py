from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.admin.routes import setup_routes as setup_admin_routes

    setup_admin_routes(app)
    app.router.add_get(
        "/health", lambda request: web.json_response({"status": "ok"})
    )
