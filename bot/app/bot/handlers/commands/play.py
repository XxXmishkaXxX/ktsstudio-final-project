import typing

from app.games.service import GameService
from app.users.models import State, User

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

    is_game_in = await app.store.games.is_active_game_in_chat(chat_id)

    if user.state == State.idle and not is_game_in:
        await app.telegram.send_message(
            chat_id,
            f"🎮 Пользователь @{user.username} запустил игру!",
        )
        service: GameService = GameService(app)
        await service.create_game(chat_id)
        return

    await app.telegram.send_message(chat_id, "В чате уже идет игра, подождите.")
