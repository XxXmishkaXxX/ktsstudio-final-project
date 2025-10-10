from passlib.hash import pbkdf2_sha256
from sqlalchemy import select

from db_core.models.admins import AdminModel

from .base import BaseAccessor


class AdminAccessor(BaseAccessor):
    async def connect(self, app) -> None:
        config_admin = app.config.admin
        email = config_admin.email
        password = config_admin.password

        if not await self.get_by_email(email):
            await self.create_admin(email, password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            return result.scalar_one_or_none()

    async def create_admin(self, email: str, password: str) -> AdminModel:
        hashed_password = pbkdf2_sha256.hash(password)

        async with self.app.database.session() as session:
            admin = AdminModel(email=email, password=hashed_password)
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return admin

    async def verify_password(
        self, password: str, hashed_password: str
    ) -> bool:
        return pbkdf2_sha256.verify(password, hashed_password)
