from unittest.mock import AsyncMock

import pytest
from db_core.models.games import GameState
from db_core.models.users import State

from app.bot.handlers.commands.play import play_command
from app.bot.handlers.commands.stop_game import stop_game_command


@pytest.mark.asyncio
async def test_stop_game_by_creator_and_non_creator(application, store):
    chat_id = 1001
    application.game_service.update_state = AsyncMock()
    application.round_service.finish_round = AsyncMock()
    store.games.get_current_round_id = AsyncMock()

    user1 = await store.users.create_or_get_user(
        {"id": 1, "username": "player1"}
    )
    user1.state = State.idle

    user2 = await store.users.create_or_get_user(
        {"id": 2, "username": "player2"}
    )
    user2.state = State.idle

    application.telegram.send_message = AsyncMock()

    await play_command(
        application, chat_id=chat_id, user=user1, chat_type="group"
    )
    game = await store.games.is_active_game_in_chat(chat_id)
    await application.cache.pool.set(f"game:{game.id}:message_id", 1)
    assert game is not None
    assert game.state == GameState.created

    await stop_game_command(
        application, chat_id=chat_id, user=user2, chat_type="group"
    )

    game = await store.games.get_game_by_id(game.id)
    assert game.state == GameState.created

    application.telegram.send_message.assert_any_await(
        chat_id, "Эта команда доступна только, начавшему игру, пользователю"
    )

    application.telegram.send_message.reset_mock()
    await stop_game_command(
        application, chat_id=chat_id, user=user1, chat_type="group"
    )

    game = await store.games.get_game_by_id(game.id)
    assert game.state == GameState.finished
