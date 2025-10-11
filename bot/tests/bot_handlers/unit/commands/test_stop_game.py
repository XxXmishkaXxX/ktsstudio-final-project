import pytest
from unittest.mock import AsyncMock, MagicMock
from db_core.models.users import User, State
from app.bot.handlers.commands.stop_game import stop_game_command


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock()
    app.game_service.get_user_created_game = AsyncMock()
    app.game_service.stop_game = AsyncMock()
    return app


@pytest.mark.asyncio
async def test_stop_game_command_private_chat(mock_app):
    user = User(id=1, username="test_user", state=State.idle)
    await stop_game_command(mock_app, chat_id=100, user=user, chat_type="private")

    mock_app.telegram.send_message.assert_awaited_once_with(
        100, "Эта команда доступна только в чате с игроками"
    )
    mock_app.store.games.is_active_game_in_chat.assert_not_awaited()
    mock_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_no_active_game(mock_app):
    mock_app.store.games.is_active_game_in_chat.return_value = None
    user = User(id=1, username="test_user", state=State.idle)

    await stop_game_command(mock_app, chat_id=200, user=user, chat_type="group")

    mock_app.telegram.send_message.assert_awaited_once_with(200, "В чате нет активных игр")
    mock_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_not_creator(mock_app):
    game = type("Game", (), {"id": 10})
    mock_app.store.games.is_active_game_in_chat.return_value = game
    mock_app.game_service.get_user_created_game.return_value = 99

    user = User(id=5, username="not_creator", state=State.in_game)

    await stop_game_command(mock_app, chat_id=300, user=user, chat_type="group")

    mock_app.telegram.send_message.assert_awaited_once_with(
        300, "Эта команда доступна только, начавшему игру, пользователю"
    )
    mock_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_creator(mock_app):
    game = type("Game", (), {"id": 20})
    mock_app.store.games.is_active_game_in_chat.return_value = game
    mock_app.game_service.get_user_created_game.return_value = 7

    user = User(id=7, username="creator", state=State.in_game)

    await stop_game_command(mock_app, chat_id=400, user=user, chat_type="group")

    mock_app.game_service.stop_game.assert_awaited_once_with(20, 400)
    mock_app.telegram.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_creator_but_different_chat_type(mock_app):
    game = type("Game", (), {"id": 30})
    mock_app.store.games.is_active_game_in_chat.return_value = game
    mock_app.game_service.get_user_created_game.return_value = 5

    user = User(id=5, username="creator", state=State.in_game)

    # Проверяем, что в "supergroup" тоже работает
    await stop_game_command(mock_app, chat_id=500, user=user, chat_type="supergroup")

    mock_app.game_service.stop_game.assert_awaited_once_with(30, 500)
