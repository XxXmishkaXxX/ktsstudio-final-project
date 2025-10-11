from sqlalchemy import select

from db_core.models.users import State, User

from .base import BaseAccessor


class UserAccessor(BaseAccessor):
    async def create_or_get_user(self, user_data: dict) -> User:
        tg_id = user_data["id"]
        username = user_data["username"]

        async with self.app.database.session() as session:
            result = await session.execute(select(User).where(User.id == tg_id))
            user = result.scalar_one_or_none()

            if user is None:
                user = User(id=tg_id, username=username)
                session.add(user)
                await session.commit()
                await session.refresh(user)

            return user

    async def set_state_user(self, tg_id: int, state: str):
        async with self.app.database.session() as session:
            user = (await session.execute(select(User).where(User.id == tg_id))).scalar_one_or_none()
            if not user:
                return

            user.state = State(state)
            await session.commit()

    async def get_state_user(self, tg_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(User.state).where(User.id == tg_id)
                )
            ).scalar_one_or_none()
