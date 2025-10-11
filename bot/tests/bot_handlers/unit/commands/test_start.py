import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.bot.handlers.commands.start import start_command

@pytest.mark.asyncio
async def test_start_command_private_chat():
    app = MagicMock()
    app.logger = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.config.bot.username = "TestBot"

    user = MagicMock()
    user.username = "test_user"

    await start_command(app, chat_id=123, user=user, chat_type="private")

    # Проверяем, что логгер вызван
    app.logger.info.assert_called_once_with(user)

    # Проверяем, что сообщение отправлено с корректными параметрами
    app.telegram.send_message.assert_awaited_once()
    args, kwargs = app.telegram.send_message.await_args
    assert args[0] == 123
    assert "test_user" in kwargs["text"]
    assert "reply_markup" in kwargs
    assert isinstance(json.loads(kwargs["reply_markup"]), dict)


@pytest.mark.asyncio
async def test_start_command_non_private_chat():
    app = MagicMock()
    app.logger = MagicMock()
    app.telegram.send_message = AsyncMock()

    user = MagicMock()
    user.username = "group_user"

    await start_command(app, chat_id=555, user=user, chat_type="group")

    # Проверяем лог
    app.logger.info.assert_called_once_with(user)

    # Проверяем, что сообщение предупреждения отправлено
    app.telegram.send_message.assert_awaited_once_with(
        555, "❌ Команда /start работает только в личном чате с ботом."
    )