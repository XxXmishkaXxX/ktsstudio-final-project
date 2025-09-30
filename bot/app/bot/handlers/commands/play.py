import json
import typing

from app.bot.keyboards import join_game
from app.bot.texts import get_game_text
from app.games.service import GameService
from app.users.models import State

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def play_command(
    app: "Application",
    chat_id: int,
    user_data: dict,
    chat_type: str,
):
    tg_id = user_data["id"]

    if chat_type == "private":
        await app.telegram.send_message(
            chat_id,
            (
                "❌ Команда /play работает только в групповых чатах.\n"
                "Добавьте бота в чат с друзьями!"
            ),
        )
        return

    state = await app.store.users.get_state_user(tg_id)
    if not state:
        user = await app.store.users.create_user(tg_id, user_data["username"])
        state = user.state

    is_game_in = await app.store.games.is_active_game_in_chat(chat_id)

    if state == State.idle and not is_game_in:
        await app.telegram.send_message(
            chat_id,
            f"🎮 Пользователь @{user_data.get('username', user_data['id'])} "
            "запустил игру!",
        )
        game = GameService(app)
        created_game = await game.create_game(chat_id)
        text = get_game_text([], [], created_game.state)
        await app.telegram.send_message(
            chat_id,
            text,
            reply_markup=json.dumps(join_game(created_game.id)),
            parse_mode="HTML",
        )
        return

    await app.telegram.send_message(chat_id, "В чате уже идет игра, подождите.")
