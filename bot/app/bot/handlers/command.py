import typing

from app.bot.handlers.commands.play import play_command
from app.bot.handlers.commands.start import start_command

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def handle_command(
    app: "Application",
    command: str,
    chat_id: int,
    user_data: dict,
    chat_type: str,
):
    if command == "/start":
        await start_command(app, chat_id, user_data, chat_type)
    elif command == "/play":
        await play_command(app, chat_id, user_data, chat_type)
