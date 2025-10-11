import pytest
from unittest.mock import AsyncMock, MagicMock
from app.bot.handlers.commands.play import play_command
from db_core.models.users import State


@pytest.mark.asyncio
async def test_play_command_private_chat():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()

    user = MagicMock()
    user.username = "player1"
    user.state = State.idle

    await play_command(app, chat_id=111, user=user, chat_type="private")

    app.telegram.send_message.assert_awaited_once_with(
        111,
        (
            "❌ Команда /play работает только в групповых чатах.\n"
            "Добавьте бота в чат с друзьями!"
        ),
    )


@pytest.mark.asyncio
async def test_play_command_starts_new_game():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock(return_value=None)
    app.logger = MagicMock()
    app.game_service.create_game = AsyncMock()

    user = MagicMock()
    user.username = "player1"
    user.state = State.idle
    user.id = 42

    await play_command(app, chat_id=222, user=user, chat_type="group")

    app.store.games.is_active_game_in_chat.assert_awaited_once_with(222)
    app.telegram.send_message.assert_any_await(
        222, "🎮 Пользователь @player1 запустил игру!"
    )
    app.game_service.create_game.assert_awaited_once_with(222, 42)


@pytest.mark.asyncio
async def test_play_command_game_already_running():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock(return_value={"id": 1})
    app.logger = MagicMock()
    app.game_service.create_game = AsyncMock()

    user = MagicMock()
    user.username = "player1"
    user.state = State.idle

    await play_command(app, chat_id=333, user=user, chat_type="group")

    app.telegram.send_message.assert_awaited_once_with(333, "В чате уже идет игра, подождите.")
    app.game_service.create_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_command_user_not_idle_but_no_game():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock(return_value=None)
    app.logger = MagicMock()
    app.game_service.create_game = AsyncMock()

    user = MagicMock()
    user.username = "player2"
    user.state = State.in_game # не idle

    await play_command(app, chat_id=444, user=user, chat_type="group")

    app.telegram.send_message.assert_awaited_once_with(444, "Вы участвуете в другой игре.")
    app.game_service.create_game.assert_not_awaited()
