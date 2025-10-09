import json
import typing

from app.bot.keyboards import main_menu
from app.bot.texts import welcome_message
from shared_models.users import User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def start_command(
    app: "Application", chat_id: int, user: User, chat_type: str
):
    app.logger.info(user)
    if chat_type != "private":
        await app.telegram.send_message(
            chat_id, "❌ Команда /start работает только в личном чате с ботом."
        )
        return

    await app.telegram.send_message(
        chat_id,
        text=welcome_message(user.username),
        reply_markup=json.dumps(main_menu(app.config.bot.username)),
    )
