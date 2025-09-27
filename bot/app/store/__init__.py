import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        pass


def setup_store(app: "Application"):
    from app.store.cache.cache import Cache
    from app.store.database.database import Database
    
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.cache = Cache(app)
    app.on_startup.append(app.cache.connect)
    app.on_cleanup.append(app.cache.disconnect)

    app.store = Store(app)
