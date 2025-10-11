import pytest
from unittest.mock import AsyncMock, MagicMock
from db_core.models.rounds import RoundState
from db_core.models.users import User, State
from app.bot.handlers.commands.answer import answer_command


@pytest.mark.asyncio
async def test_answer_command_no_game():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock(return_value=None)
    app.round_service = MagicMock()

    user = User(id=1, username="test", state=State.in_game)

    await answer_command(app, chat_id=123, chat_type="group", answer="42", user=user)

    app.telegram.send_message.assert_not_awaited()
    app.round_service.buzzer_answer_question.assert_not_called()
    app.round_service.team_answer_question.assert_not_called()


@pytest.mark.asyncio
async def test_answer_command_buzzer_answer():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock()
    app.store.rounds.get_round_state = AsyncMock()
    app.round_service = MagicMock()
    app.round_service.buzzer_answer_question = AsyncMock()
    app.round_service.team_answer_question = AsyncMock()

    game = MagicMock()
    game.id = 1
    game.current_round_id = 10
    app.store.games.is_active_game_in_chat.return_value = game
    app.store.rounds.get_round_state.return_value = RoundState.buzzer_answer

    user = User(id=5, username="buzzer_user", state=State.in_game)

    await answer_command(app, chat_id=42, chat_type="group", answer="Answer", user=user)

    app.round_service.buzzer_answer_question.assert_awaited_once_with(1, 5, "Answer")
    app.round_service.team_answer_question.assert_not_awaited()


@pytest.mark.asyncio
async def test_answer_command_team_play():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()
    app.store.games.is_active_game_in_chat = AsyncMock()
    app.store.rounds.get_round_state = AsyncMock()
    app.round_service = MagicMock()
    app.round_service.buzzer_answer_question = AsyncMock()
    app.round_service.team_answer_question = AsyncMock()

    game = MagicMock()
    game.id = 10
    game.current_round_id = 100
    app.store.games.is_active_game_in_chat.return_value = game
    app.store.rounds.get_round_state.return_value = RoundState.team_play

    user = User(id=9, username="team_user", state=State.in_game)

    await answer_command(app, chat_id=99, chat_type="group", answer="Go!", user=user)

    app.round_service.team_answer_question.assert_awaited_once_with(10, 99, 9, "Go!")
    app.round_service.buzzer_answer_question.assert_not_awaited()


@pytest.mark.asyncio
async def test_answer_command_private_chat():
    app = MagicMock()
    app.telegram.send_message = AsyncMock()

    user = User(id=1, username="private_user", state=State.idle)

    await answer_command(app, chat_id=111, chat_type="private", answer="42", user=user)

    app.telegram.send_message.assert_awaited_once()
