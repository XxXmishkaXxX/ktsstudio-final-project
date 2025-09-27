import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.questions.accessor import QuestionsAccessor

        self.admins = AdminAccessor(app)
        self.questions = QuestionsAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.store = Store(app)
    app.on_startup.append(app.store.admins.connect)
