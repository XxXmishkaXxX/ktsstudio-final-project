import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from db_core.accessors.games import GameAccessor
        from db_core.accessors.questions import QuestionAccessor
        from db_core.accessors.rounds import RoundAccessor
        from db_core.accessors.teams import TeamAccessor
        from db_core.accessors.users import UserAccessor

        self.users = UserAccessor(app)
        self.games = GameAccessor(app)
        self.teams = TeamAccessor(app)
        self.rounds = RoundAccessor(app)
        self.questions = QuestionAccessor(app)


def setup_store(app: "Application"):
    from app.store.cache.cache import Cache
    from db_core.database.db import Database

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.cache = Cache(app)
    app.on_startup.append(app.cache.connect)
    app.on_cleanup.append(app.cache.disconnect)

    app.store = Store(app)
