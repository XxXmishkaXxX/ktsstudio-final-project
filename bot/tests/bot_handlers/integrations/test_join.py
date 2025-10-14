from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_join_to_game(application, store):
    chat_id = 1003
    tg_id = 42

    game = await store.games.create_game_with_teams(chat_id)
    team1, team2 = await store.teams.get_game_teams(game.id)

    await store.users.create_or_get_user(
        {"id": tg_id, "username": f"user{tg_id}"}
    )

    for i in range(2, 7):
        await store.users.create_or_get_user({"id": i, "username": f"user{i}"})

    application.game_service.update_state = AsyncMock()

    await application.game_service.join_to_game(
        game.id, team2.id, tg_id, chat_id
    )
    team_id = await store.teams.get_team_by_user_id(game.id, tg_id)
    assert team_id == team2.id

    with pytest.raises(Exception, match="Вы уже находитесь в этой команде"):
        await application.game_service.join_to_game(
            game.id, team2.id, tg_id, chat_id
        )

    with pytest.raises(Exception, match="Команда не найдена"):
        await application.game_service.join_to_game(
            game.id, 999, tg_id, chat_id
        )

    for i in range(2, 7):
        await store.teams.join_team(team1.id, i)

    with pytest.raises(Exception, match="В команде нет свободных мест"):
        await application.game_service.join_to_game(
            game.id, team1.id, tg_id + 1, chat_id
        )
