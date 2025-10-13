from unittest.mock import AsyncMock, patch

import pytest

from app.bot.handlers.callback import handle_callback
from app.bot.handlers.command import handle_command


@pytest.mark.asyncio
@patch("app.bot.handlers.callback.join_game_callback", new_callable=AsyncMock)
@patch(
    "app.bot.handlers.callback.press_buzzer_callback", new_callable=AsyncMock
)
async def test_handle_callback_invokes_join_and_buzzer(mock_buzzer, mock_join):
    app = AsyncMock()
    app.store.users.create_or_get_user = AsyncMock(return_value={"id": 1})

    # ---- join ----
    await handle_callback(
        app=app,
        callback_type="join",
        game_id=10,
        chat_id=20,
        callback_id=30,
        message_id=40,
        user_data={"id": 1},
        team=2,
        team_num=1,
    )
    app.store.users.create_or_get_user.assert_awaited_once_with({"id": 1})
    mock_join.assert_awaited_once_with(app, 10, 20, 30, 40, {"id": 1}, 2, 1)

    # ---- buzzer ----
    app.store.users.create_or_get_user.reset_mock()
    mock_join.reset_mock()
    await handle_callback(
        app=app,
        callback_type="buzzer",
        game_id=10,
        chat_id=20,
        callback_id=99,
        message_id=77,
        user_data={"id": 1},
        round_id=15,
    )
    app.store.users.create_or_get_user.assert_awaited_once()
    mock_buzzer.assert_awaited_once_with(app, 15, 99, {"id": 1})


@pytest.mark.asyncio
async def test_handle_callback_ignores_unknown_type():
    app = AsyncMock()
    app.store.users.create_or_get_user = AsyncMock(return_value={"id": 1})
    # неизвестный тип не должен ничего вызвать
    await handle_callback(
        app=app,
        callback_type="unknown",
        game_id=1,
        chat_id=1,
        callback_id=1,
        message_id=1,
        user_data={"id": 123},
    )
    app.store.users.create_or_get_user.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.bot.handlers.command.start_command", new_callable=AsyncMock)
@patch("app.bot.handlers.command.play_command", new_callable=AsyncMock)
@patch("app.bot.handlers.command.stop_game_command", new_callable=AsyncMock)
@patch("app.bot.handlers.command.answer_command", new_callable=AsyncMock)
async def test_handle_command_invokes_correct_handlers(
    mock_answer, mock_stop, mock_play, mock_start
):
    app = AsyncMock()
    app.store.users.create_or_get_user = AsyncMock(return_value={"id": 42})
    chat_id, user_data, chat_type = 10, {"id": 42}, "private"

    # ---- /start ----
    await handle_command(app, "/start", chat_id, user_data, chat_type)
    mock_start.assert_awaited_once_with(app, chat_id, {"id": 42}, chat_type)

    # ---- /play ----
    await handle_command(app, "/play", chat_id, user_data, chat_type)
    mock_play.assert_awaited_once_with(app, chat_id, {"id": 42}, chat_type)

    # ---- /stop_game ----
    await handle_command(app, "/stop_game", chat_id, user_data, chat_type)
    mock_stop.assert_awaited_once_with(app, chat_id, {"id": 42}, chat_type)

    # ---- /ans ----
    await handle_command(
        app,
        "/ans",
        chat_id,
        user_data,
        chat_type,
        args="answer_text",
    )
    mock_answer.assert_awaited_once_with(
        app, chat_id, chat_type, "answer_text", {"id": 42}
    )

    app.store.users.create_or_get_user.assert_awaited()


@pytest.mark.asyncio
async def test_handle_command_ignores_unknown_command():
    app = AsyncMock()
    app.store.users.create_or_get_user = AsyncMock(return_value={"id": 1})
    await handle_command(
        app,
        "/unknown",
        chat_id=1,
        user_data={"id": 1},
        chat_type="private",
    )
    app.store.users.create_or_get_user.assert_awaited_once()
