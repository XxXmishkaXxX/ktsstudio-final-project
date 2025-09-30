import typing

from app.users.models import User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def create_or_get_user(app: "Application", user_data: dict) -> User:
    username = user_data["username"]
    tg_id = user_data["id"]
    user = await app.store.users.get_user(tg_id)

    if not user:
        user = await app.store.users.create_user(tg_id, username)
        await app.store.users.set_state_user(tg_id, "idle")

    return user
