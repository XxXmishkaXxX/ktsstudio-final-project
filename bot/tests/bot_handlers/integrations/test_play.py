from unittest.mock import AsyncMock

import pytest
from db_core.models.games import GameState
from db_core.models.users import State

from app.bot.handlers.commands.play import play_command


@pytest.mark.asyncio
async def test_play_command_creates_game_and_teams(application, store):
    chat_id = 1000
    tg_user_id = 42

    application.game_service.update_state = AsyncMock()
    user = await store.users.create_or_get_user(
        {"id": tg_user_id, "username": "player1"}
    )
    user.state = State.idle

    game_in_chat = await store.games.is_active_game_in_chat(chat_id)
    assert game_in_chat is None

    application.telegram.send_message = AsyncMock()

    await play_command(
        application, chat_id=chat_id, user=user, chat_type="group"
    )

    game = await application.store.games.is_active_game_in_chat(chat_id)
    assert game is not None
    assert game.state == GameState.created

    teams = await application.store.teams.get_game_teams(game.id)
    assert len(teams) == 2

    application.telegram.send_message.assert_any_await(
        chat_id, f"🎮 Пользователь @{user.username} запустил игру!"
    )
