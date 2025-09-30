from app.store.base.accessor import BaseAccessor
from app.users.models import State, User
from sqlalchemy import select


class UserAccessor(BaseAccessor):
    async def create_user(self, tg_id: int, username: str):
        async with self.app.database.session() as session:
            user = User(id=tg_id, username=username)
            session.add(user)
            await session.commit()
            return user

    async def get_user(self, tg_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(select(User).where(User.id == tg_id))
            ).scalar_one_or_none()

    async def set_state_user(self, tg_id: int, state: str):
        async with self.app.database.session() as session:
            user = await self.get_user(tg_id)
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
