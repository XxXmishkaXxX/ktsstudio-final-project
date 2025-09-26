from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_rabbitmq():
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock
