from typing import Any

from db_core.models.base import BaseModel
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Database:
    def __init__(self, app) -> None:
        self.app = app
        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        db_config = self.app.config.db

        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                username=db_config.user,
                password=db_config.password,
                host=db_config.host,
                port=db_config.port,
                database=db_config.database,
            ),
        )

        self.session = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()
