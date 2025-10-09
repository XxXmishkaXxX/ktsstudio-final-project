import os
import pytest
from unittest.mock import AsyncMock
from app.web.app import setup_app



@pytest.fixture(scope="session")
async def application(mock_rabbitmq):
    app = setup_app(
        config_path=os.path.join(os.path.dirname(__file__), "config.yml")
    )

    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.rmq = mock_rabbitmq
    yield app


@pytest.fixture(scope="session")
def mock_rabbitmq():
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock

@pytest.fixture
def reset_rabbitmq(application, mock_rabbitmq):
    application.rmq = mock_rabbitmq
    mock_rabbitmq.publish.reset_mock()
    return mock_rabbitmq

@pytest.fixture
async def client(aiohttp_client, application):
    return await aiohttp_client(application)
