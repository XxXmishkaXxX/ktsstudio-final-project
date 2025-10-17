import asyncio
import os

import pytest
from db_core.database.db import Database

from app.rmq import RabbitMQ
from app.store.cache.cache import Cache
from app.web.app import setup_app

from .fixtures import *  # noqa: F403


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
async def application():
    app = setup_app(
        config_path=os.path.join(os.path.dirname(__file__), "test_config.yml")
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.database = Database(app)

    app.cache = Cache(app)
    await app.cache.connect()

    await app.database.connect()
    async with app.database.engine.begin() as conn:
        await conn.run_sync(app.database._db.metadata.create_all)

    app.rmq = RabbitMQ(app)
    await app.rmq.connect()

    yield app

    async with app.database.engine.begin() as conn:
        await conn.run_sync(app.database._db.metadata.drop_all)

    await app.cache.pool.flushdb()
    await app.database.disconnect()
    await app.rmq.close()


@pytest.fixture
def store(application):
    return application.store


@pytest.fixture
def config(application):
    return application.config


@pytest.fixture
def rmq(application):
    return application.rmq
