import pytest
from db_core.models.games import Game, GameState
from db_core.models.teams import Team
from db_core.models.users import User, State
from unittest.mock import AsyncMock
from app.bot.handlers.commands.play import play_command



@pytest.mark.asyncio
async def test_play_command_creates_game_and_teams(application, store):
    chat_id = 1000
    tg_user_id = 42

    application.game_service.update_state = AsyncMock()
    # Создаём пользователя
    user = await store.users.create_or_get_user(
        {"id": tg_user_id, "username": "player1"}
    )
    user.state = State.idle

    # Проверяем, что игры в чате нет
    game_in_chat = await store.games.is_active_game_in_chat(chat_id)
    assert game_in_chat is None

    # Мокаем telegram
    application.telegram.send_message = AsyncMock()

    # Вызываем команду /play
    await play_command(application, chat_id=chat_id, user=user, chat_type="group")

    # Проверяем, что игра создалась
    game = await application.store.games.is_active_game_in_chat(chat_id)
    assert game is not None
    assert game.state == GameState.created

    # Проверяем, что созданы две команды
    teams = await application.store.teams.get_game_teams(game.id)
    assert len(teams) == 2

    # Можно проверить сообщение в телеграм
    application.telegram.send_message.assert_any_await(
        chat_id, f"🎮 Пользователь @{user.username} запустил игру!"
    )
