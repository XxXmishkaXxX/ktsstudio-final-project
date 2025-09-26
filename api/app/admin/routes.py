import typing

from app.admin.views import AdminCurrentView
from app.admin.views import AdminLoginView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):

    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)