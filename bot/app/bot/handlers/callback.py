import typing

from app.bot.handlers.callbacks.join import join_game_callback
from app.bot.handlers.utils.users import create_or_get_user

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def handle_callback(
    app: "Application",
    callback_type: str,
    game_id: int,
    chat_id: int,
    callback_id: int,
    message_id: int,
    user_data: dict,
    **kwargs,
):
    user = await create_or_get_user(app, user_data)

    if callback_type == "join":
        team = kwargs.get("team")
        await join_game_callback(
            app, game_id, chat_id, callback_id, message_id, user, team
        )
