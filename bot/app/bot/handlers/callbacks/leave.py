import typing

from db_core.models.games import GameState
from db_core.models.users import State, User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def leave_game_callback(
    app: "Application",
    game_id: int,
    chat_id: int,
    callback_id: int,
    message_id: int,
    user: User,
):
    try:
        game_state = await app.store.games.get_game_state(game_id)
        if game_state != GameState.finished:
            await app.game_service.leave_game(game_id, user.id)
            await app.store.users.set_state_user(user.id, State.idle)

            await app.game_service.update_state(game_id, chat_id, message_id)

            await app.telegram.answer_callback_query(
                callback_id, "Вы вышли из игры"
            )
            return
        await app.telegram.answer_callback_query(
            callback_id, "Игра уже окончена"
        )
    except Exception as e:
        await app.telegram.answer_callback_query(callback_id, str(e))
