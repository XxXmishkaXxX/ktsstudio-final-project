import os

import pytest
from app.web.app import setup_app

from .fixtures import *  # noqa: F403


@pytest.fixture
def application(mock_rabbitmq):
    app = setup_app(
        config_path=os.path.join(os.path.dirname(__file__), "config.yml")
    )

    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.rmq = mock_rabbitmq

    return app


@pytest.fixture
async def client(aiohttp_client, application):
    return await aiohttp_client(application)
