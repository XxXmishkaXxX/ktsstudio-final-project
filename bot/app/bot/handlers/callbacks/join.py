import typing

from db_core.models.users import State, User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def join_game_callback(
    app: "Application",
    game_id: int,
    chat_id: int,
    callback_id: int,
    message_id: int,
    user: User,
    team: int,
):
    try:
        await app.store.users.set_state_user(user.id, State.in_game)
        team_id = await app.game_service.join_to_game(
            game_id, team, user.id, chat_id, message_id
        )
        await app.telegram.answer_callback_query(
            callback_id, f"Вы присоединились в команду {team_id}"
        )
    except Exception as e:
        await app.telegram.answer_callback_query(callback_id, str(e))
    else:
        return
