from unittest.mock import MagicMock

import pytest
from db_core.models.rounds import RoundState
from db_core.models.users import State, User

from app.bot.handlers.commands.answer import answer_command


@pytest.mark.asyncio
async def test_answer_command_no_game(mocked_app):
    mocked_app.store.games.is_active_game_in_chat.return_value = None

    user = User(id=1, username="test", state=State.in_game)

    await answer_command(
        mocked_app, chat_id=123, chat_type="group", answer="42", user=user
    )

    mocked_app.telegram.send_message.assert_not_awaited()
    mocked_app.round_service.buzzer_answer_question.assert_not_called()
    mocked_app.round_service.team_answer_question.assert_not_called()


@pytest.mark.asyncio
async def test_answer_command_buzzer_answer(mocked_app):
    game = MagicMock()
    game.id = 1
    game.current_round_id = 10
    mocked_app.store.games.is_active_game_in_chat.return_value = game
    mocked_app.store.rounds.get_round_state.return_value = (
        RoundState.buzzer_answer
    )

    user = User(id=5, username="buzzer_user", state=State.in_game)

    await answer_command(
        mocked_app, chat_id=42, chat_type="group", answer="Answer", user=user
    )

    mocked_app.round_service.buzzer_answer_question.assert_awaited_once_with(
        1, 5, "Answer"
    )
    mocked_app.round_service.team_answer_question.assert_not_awaited()


@pytest.mark.asyncio
async def test_answer_command_team_play(mocked_app):
    game = MagicMock()
    game.id = 10
    game.current_round_id = 100
    mocked_app.store.games.is_active_game_in_chat.return_value = game
    mocked_app.store.rounds.get_round_state.return_value = RoundState.team_play

    user = User(id=9, username="team_user", state=State.in_game)

    await answer_command(
        mocked_app, chat_id=99, chat_type="group", answer="Go!", user=user
    )

    mocked_app.round_service.team_answer_question.assert_awaited_once_with(
        10, 99, 9, "Go!"
    )
    mocked_app.round_service.buzzer_answer_question.assert_not_awaited()


@pytest.mark.asyncio
async def test_answer_command_private_chat(mocked_app):
    user = User(id=1, username="private_user", state=State.idle)

    await answer_command(
        mocked_app, chat_id=111, chat_type="private", answer="42", user=user
    )

    mocked_app.telegram.send_message.assert_awaited_once()
