import pytest
from unittest.mock import AsyncMock
import json
from db_core.models.rounds import RoundState
from app.bot.handlers.commands.answer import answer_command
from app.bot.handlers.callbacks.buzzer import press_buzzer_callback

@pytest.mark.asyncio
async def test_buzzer_answer(application, store):
    chat_id = 1777

    player1 = await store.users.create_or_get_user({"id": 1, "username": "player1"})
    player2 = await store.users.create_or_get_user({"id": 2, "username": "player2"})

    game = await store.games.create_game_with_teams(chat_id)
    game_id = game.id
    teams = await store.teams.get_game_teams(game.id)
    team1, _ = teams
    await store.teams.join_team(team1.id, player1.id)
    await store.teams.join_team(team1.id, player2.id)

    payload = {"text": "2+2?", "answers":[{"text": "4", "points": 10, "position": 1}]}
    await store.questions.create_question(payload)

    round_ = await store.rounds.create_round(game_id, 1)
    round_id = round_.id

    allowed_ids = [player1.id, player2.id]
    application.round_service.get_current_buzzers = AsyncMock(return_value=allowed_ids)

    application.telegram.answer_callback_query = AsyncMock()

    await press_buzzer_callback(application, round_id, callback_id=101, user=player1)
    
    application.telegram.answer_callback_query.assert_awaited_with(101, "Вы первый!")

    await store.rounds.set_round_state(round_.id, RoundState.buzzer_answer)

    await answer_command(application, chat_id, "group", "4", player1)

    round_in_db = await store.rounds.get_round_by_id(round_id)
    assert round_in_db.current_team_id == team1.id
    assert round_in_db.current_buzzer_id is None or round_in_db.state == RoundState.team_play


@pytest.mark.asyncio
async def test_team_answer(application, store):
    chat_id = 666

    # Создаём игроков команды
    players_team1 = [await store.users.create_or_get_user({"id": i, "username": f"p{i}"}) for i in range(1, 6)]

    # Создаём игру и команду
    game = await store.games.create_game_with_teams(chat_id)
    game_id = game.id
    teams = await store.teams.get_game_teams(game.id)
    team1, _ = teams
    for player in players_team1:
        await store.teams.join_team(team1.id, player.id)

    payload = {"text": "2+2?", "answers":[{"text": "4", "points": 10, "position": 1}]}
    await store.questions.create_question(payload)

    round_ = await store.rounds.create_round(game_id, 1)
    round_id = round_.id
    await store.rounds.set_round_state(round_id, RoundState.team_play)
    round_ = await store.rounds.get_round_by_id(round_id)
    round_.current_team_id = team1.id
    await store.rounds.update_round(round_)

    application.telegram.send_message = AsyncMock()
    application.telegram.answer_callback_query = AsyncMock()
    application.renderer.render_in_progress = AsyncMock()

    await answer_command(application, chat_id, "group", "4", players_team1[0])

    opened_answers_json = await application.cache.pool.get(f"round:{round_.id}:opened_answers")
    opened_answers = json.loads(opened_answers_json)
    assert opened_answers, "Ответы команды должны быть зарегистрированы"

    round_in_db = await store.rounds.get_round_by_id(round_id)
    assert round_in_db.state in [RoundState.team_play, RoundState.finished]