import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rmq import RabbitMQ
from app.rmq.rmq_callback import rmq_callback
from app.rmq.utils import (
    extract_callback_data,
    extract_message_data,
    parse_json_body,
)


def test_parse_json_body_valid():
    message = MagicMock()
    message.body = json.dumps({"key": "value"}).encode()
    assert parse_json_body(message) == {"key": "value"}


def test_parse_json_body_invalid():
    message = MagicMock()
    message.body = b"{invalid"

    with pytest.raises(ValueError, match=r"^Invalid JSON in message body:"):
        parse_json_body(message)


def test_extract_callback_data():
    payload = {
        "callback_query": {
            "message": {"chat": {"id": 1}, "message_id": 2},
            "id": "cb123",
            "from": {"id": 42, "name": "User"},
            "data": json.dumps(
                {"type": "join", "game": 55, "round": 10, "team": 1}
            ),
        }
    }
    data = extract_callback_data(payload)
    assert data["chat_id"] == 1
    assert data["callback_type"] == "join"
    assert data["team"] == 1


def test_extract_message_data_with_command():
    payload = {
        "message": {
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 123},
            "text": "/start arg1 arg2",
            "entities": [{"type": "bot_command", "offset": 0, "length": 6}],
        }
    }
    data = extract_message_data(payload)
    assert data["command"] == "/start"
    assert data["args"] == "arg1 arg2"


@pytest.mark.asyncio
async def test_rmq_callback_logs_exception(application):
    application.logger = MagicMock()

    message = MagicMock()
    mock_process_cm = AsyncMock()
    mock_process_cm.__aenter__.side_effect = Exception("boom")
    mock_process_cm.__aexit__.return_value = None
    message.process.return_value = mock_process_cm

    await rmq_callback(message, application)
    application.logger.exception.assert_called_once()


@pytest.mark.asyncio
@patch("app.rmq.rmq_callback.handle_callback", new_callable=AsyncMock)
@patch("app.rmq.rmq_callback.handle_command", new_callable=AsyncMock)
async def test_rmq_callback_invokes_correct_handler(
    mock_command, mock_callback, application
):
    message = MagicMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = None
    mock_context_manager.__aexit__.return_value = None
    message.process.return_value = mock_context_manager

    # ---- Тестируем callback_query ----
    payload_callback = {
        "callback_query": {
            "message": {"chat": {"id": 1}, "message_id": 10},
            "id": "cb123",
            "from": {"id": 100},
            "data": json.dumps({"type": "join", "game": 5, "t_num": 1}),
        }
    }

    with (
        patch(
            "app.rmq.rmq_callback.parse_json_body",
            return_value=payload_callback,
        ),
        patch(
            "app.rmq.rmq_callback.extract_callback_data",
            return_value={
                "callback_type": "ANSWER",
                "game_id": 5,
                "chat_id": 1,
                "callback_id": "cb123",
                "message_id": 10,
                "user_data": {"id": 100},
                "team_num": 1,
                "team": None,
                "round_id": None,
            },
        ),
    ):
        await rmq_callback(message, application)
        mock_callback.assert_awaited_once()

    # ---- Тестируем message ----
    payload_message = {
        "message": {
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 100},
            "text": "/start",
            "entities": [{"type": "bot_command", "offset": 0, "length": 6}],
        }
    }

    with (
        patch(
            "app.rmq.rmq_callback.parse_json_body", return_value=payload_message
        ),
        patch(
            "app.rmq.rmq_callback.extract_message_data",
            return_value={
                "command": "/start",
                "args": "",
                "chat_id": 1,
                "chat_type": "private",
                "user_data": {"id": 100},
            },
        ),
    ):
        await rmq_callback(message, application)
        mock_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_rabbitmq_consume_without_queue(rmq):
    rmq = RabbitMQ(MagicMock, "localhost", 1111, "user", "pass", "test-queue")
    with pytest.raises(RuntimeError):
        await rmq.consume(AsyncMock())


@pytest.mark.asyncio
async def test_rabbitmq_close(application):
    rmq = RabbitMQ(application, "localhost", 1111, "user", "pass", "test-queue")
    rmq._connection = AsyncMock()

    await rmq.close()
    rmq._connection.close.assert_called_once()
