import typing

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
    pass
