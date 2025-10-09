import typing

from shared_models.users import State, User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def play_command(
    app: "Application",
    chat_id: int,
    user: User,
    chat_type: str,
):
    if chat_type == "private":
        await app.telegram.send_message(
            chat_id,
            (
                "❌ Команда /play работает только в групповых чатах.\n"
                "Добавьте бота в чат с друзьями!"
            ),
        )
        return

    game = await app.store.games.is_active_game_in_chat(chat_id)

    app.logger.info(game)

    if user.state == State.idle and not game:
        await app.telegram.send_message(
            chat_id,
            f"🎮 Пользователь @{user.username} запустил игру!",
        )
        await app.game_service.create_game(chat_id, user.id)
        return

    await app.telegram.send_message(chat_id, "В чате уже идет игра, подождите.")
