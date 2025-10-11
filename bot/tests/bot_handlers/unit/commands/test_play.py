import pytest

from app.bot.handlers.commands.play import play_command


@pytest.mark.asyncio
async def test_play_command_private_chat(mocked_app, idle_user):
    await play_command(
        mocked_app, chat_id=111, user=idle_user, chat_type="private"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        111,
        (
            "❌ Команда /play работает только в групповых чатах.\n"
            "Добавьте бота в чат с друзьями!"
        ),
    )


@pytest.mark.asyncio
async def test_play_command_starts_new_game(mocked_app, idle_user):
    mocked_app.store.games.is_active_game_in_chat.return_value = None

    await play_command(
        mocked_app, chat_id=222, user=idle_user, chat_type="group"
    )

    mocked_app.store.games.is_active_game_in_chat.assert_awaited_once_with(222)
    mocked_app.telegram.send_message.assert_any_await(
        222, "🎮 Пользователь @player1 запустил игру!"
    )
    mocked_app.game_service.create_game.assert_awaited_once_with(
        222, idle_user.id
    )


@pytest.mark.asyncio
async def test_play_command_game_already_running(mocked_app, idle_user):
    mocked_app.store.games.is_active_game_in_chat.return_value = {"id": 1}

    await play_command(
        mocked_app, chat_id=333, user=idle_user, chat_type="group"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        333, "В чате уже идет игра, подождите."
    )
    mocked_app.game_service.create_game.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_command_user_not_idle_but_no_game(mocked_app, in_game_user):
    mocked_app.store.games.is_active_game_in_chat.return_value = None

    await play_command(
        mocked_app, chat_id=444, user=in_game_user, chat_type="group"
    )

    mocked_app.telegram.send_message.assert_awaited_once_with(
        444, "Вы участвуете в другой игре."
    )
    mocked_app.game_service.create_game.assert_not_awaited()
