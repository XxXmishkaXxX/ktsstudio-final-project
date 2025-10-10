import asyncio
import os

import pytest
from aiohttp.test_utils import TestClient
from db_core.database.db import Database
from app.web.app import setup_app


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

    await app.database.connect()
    async with app.database.engine.begin() as conn:
        await conn.run_sync(app.database._db.metadata.create_all)

    await app.store.admins.connect(app)
    yield app

    async with app.database.engine.begin() as conn:
        await conn.run_sync(app.database._db.metadata.drop_all)

    await app.database.disconnect()
    await app.store.admins.disconnect(app)


@pytest.fixture
def store(application):
    return application.store


@pytest.fixture
def config(application):
    return application.config


@pytest.fixture
def client(aiohttp_client, application, event_loop):
    return event_loop.run_until_complete(aiohttp_client(application))


@pytest.fixture
async def auth_cli(client: TestClient, config) -> TestClient:
    await client.post(
        path="/admin.login",
        json={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    return client
