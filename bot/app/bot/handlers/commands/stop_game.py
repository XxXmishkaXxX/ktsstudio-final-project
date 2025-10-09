import typing

from db_core.models.users import User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def stop_game_command(
    app: "Application", chat_id: int, user: User, chat_type: str
):
    if chat_type == "private":
        await app.telegram.send_message(
            chat_id, "Эта команда доступна только в чате с игроками"
        )
        return

    game = await app.store.games.is_active_game_in_chat(chat_id)

    if not game:
        await app.telegram.send_message(chat_id, "В чате нет активных игр")
        return

    user_created_game = await app.game_service.get_user_created_game(game.id)

    if user.id != user_created_game:
        await app.telegram.send_message(
            chat_id, "Эта команда доступна только, начавшему игру, пользователю"
        )
        return

    await app.game_service.stop_game(game.id, chat_id)
