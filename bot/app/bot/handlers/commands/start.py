import json
import typing

from app.bot.keyboards import main_menu
from app.bot.texts import welcome_message

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def start_command(
    app: "Application", chat_id: int, user_data: dict, chat_type: str
):
    if chat_type != "private":
        await app.telegram.send_message(
            chat_id, "❌ Команда /start работает только в личном чате с ботом."
        )
        return

    tg_id = user_data["id"]
    user = await app.store.users.get_user(tg_id)

    if not user:
        username = user_data.get("username") or user_data.get(
            "first_name", "игрок"
        )
        await app.store.users.create_user(tg_id, username)
        await app.store.users.set_state_user(tg_id, "idle")
    else:
        username = user.username

    await app.telegram.send_message(
        chat_id,
        text=welcome_message(username),
        reply_markup=json.dumps(main_menu(app.config.bot.username)),
    )
