import pytest
from unittest.mock import AsyncMock, call
from db_core.models.users import User
from app.bot.handlers.callbacks.buzzer import press_buzzer_callback 

@pytest.mark.asyncio
async def test_press_buzzer_multiple_players(application, store):
    chat_id = 1323

    player1 = await store.users.create_or_get_user({"id": 1, "username": "player1"})
    player2 = await store.users.create_or_get_user({"id": 2, "username": "player2"})
    player3 = await store.users.create_or_get_user({"id": 3, "username": "player3"})

    payload = {
        "text": "Попытка без авторизации?",
        "answers": [
            {"text": "A", "points": 10, "position": 1},
            {"text": "B", "points": 5, "position": 2},
            {"text": "C", "points": 3, "position": 3},
            {"text": "D", "points": 2, "position": 4},
            {"text": "E", "points": 1, "position": 5},
        ],
    }
    await store.questions.create_question(payload)

    game = await store.games.create_game_with_teams(chat_id)
    game_id = game.id

    round_ = await store.rounds.create_round(game_id, 1)
    round_id = round_.id

    allowed_ids = [player1.id, player2.id]
    application.round_service.get_current_buzzers = AsyncMock(return_value=allowed_ids)

    application.telegram.answer_callback_query = AsyncMock()

    await press_buzzer_callback(application, round_id, callback_id=101, user=player1)
    await press_buzzer_callback(application, round_id, callback_id=102, user=player2)
    await press_buzzer_callback(application, round_id, callback_id=103, user=player3)

    application.telegram.answer_callback_query.assert_has_awaits([
        call(101, "Вы первый!"),
        call(102, "Кто-то уже нажал кнопку"),
        call(103, "Вы не участвуете в faceoff")
    ])

    round_in_db = await store.rounds.get_round_by_id(round_id)
    assert round_in_db.current_buzzer_id == player1.id
