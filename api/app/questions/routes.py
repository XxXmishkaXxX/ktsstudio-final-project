import typing

from app.questions.views import QuestionsView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/questions", QuestionsView)
