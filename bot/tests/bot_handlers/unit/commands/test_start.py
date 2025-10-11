import json

import pytest

from app.bot.handlers.commands.start import start_command


@pytest.mark.asyncio
async def test_start_command_private_chat(mocked_app, private_user):
    await start_command(
        mocked_app, chat_id=123, user=private_user, chat_type="private"
    )

    # Проверяем, что логгер вызван
    mocked_app.logger.info.assert_called_once_with(private_user)

    # Проверяем, что сообщение отправлено с корректными параметрами
    mocked_app.telegram.send_message.assert_awaited_once()
    args, kwargs = mocked_app.telegram.send_message.await_args
    assert args[0] == 123
    assert "test_user" in kwargs["text"]
    assert "reply_markup" in kwargs
    assert isinstance(json.loads(kwargs["reply_markup"]), dict)


@pytest.mark.asyncio
async def test_start_command_non_private_chat(mocked_app, group_user):
    await start_command(
        mocked_app, chat_id=555, user=group_user, chat_type="group"
    )

    mocked_app.logger.info.assert_called_once_with(group_user)

    mocked_app.telegram.send_message.assert_awaited_once_with(
        555, "❌ Команда /start работает только в личном чате с ботом."
    )
