from app.store.base.accessor import BaseAccessor
from app.users.models import User
from sqlalchemy import select


class UserAccessor(BaseAccessor):
    async def create_user(self, tg_id: int, username: str):
        async with self.app.database.session() as session:
            user = User(tg_id=tg_id, username=username)
            session.add(user)
            await session.commit()

    async def get_user(self, tg_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(select(User).where(User.tg_id == tg_id))
            ).scalar_one_or_none()
