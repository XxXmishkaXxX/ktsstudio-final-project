from unittest.mock import MagicMock

import pytest

from app.bot.handlers.commands.stop_game import stop_game_command


@pytest.mark.asyncio
async def test_stop_game_command_private_chat(mocked_app, idle_user):
    await stop_game_command(
        mocked_app, chat_id=100, user=idle_user, chat_type="private"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        100, "Эта команда доступна только в чате с игроками"
    )
    mocked_app.store.games.is_active_game_in_chat.assert_not_awaited()
    mocked_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_no_active_game(mocked_app, idle_user):
    mocked_app.store.games.is_active_game_in_chat.return_value = None

    await stop_game_command(
        mocked_app, chat_id=200, user=idle_user, chat_type="group"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        200, "В чате нет активных игр"
    )
    mocked_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_not_creator(mocked_app, not_creator_user):
    game = MagicMock(id=10)
    mocked_app.store.games.is_active_game_in_chat.return_value = game
    mocked_app.game_service.get_user_created_game.return_value = 99  # другой ID

    await stop_game_command(
        mocked_app, chat_id=300, user=not_creator_user, chat_type="group"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        300, "Эта команда доступна только, начавшему игру, пользователю"
    )
    mocked_app.game_service.stop_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_creator(mocked_app, creator_user):
    game = MagicMock(id=20)
    mocked_app.store.games.is_active_game_in_chat.return_value = game
    mocked_app.game_service.get_user_created_game.return_value = creator_user.id

    await stop_game_command(
        mocked_app, chat_id=400, user=creator_user, chat_type="group"
    )

    mocked_app.game_service.stop_game.assert_awaited_once_with(20, 400)
    mocked_app.telegram.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_stop_game_command_creator_supergroup(mocked_app, creator_user):
    game = MagicMock(id=30)
    mocked_app.store.games.is_active_game_in_chat.return_value = game
    mocked_app.game_service.get_user_created_game.return_value = creator_user.id

    await stop_game_command(
        mocked_app, chat_id=500, user=creator_user, chat_type="supergroup"
    )

    mocked_app.game_service.stop_game.assert_awaited_once_with(30, 500)
