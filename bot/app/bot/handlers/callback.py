import typing

from app.bot.handlers.callbacks.buzzer import press_buzzer_callback
from app.bot.handlers.callbacks.join import join_game_callback

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
    user = await app.store.users.create_or_get_user(user_data)
    match callback_type:
        case "join":
            team = kwargs.get("team")
            await join_game_callback(
                app, game_id, chat_id, callback_id, message_id, user, team
            )
        case "buzzer":
            round_id = kwargs.get("round_id")
            await press_buzzer_callback(app, round_id, callback_id, user)
