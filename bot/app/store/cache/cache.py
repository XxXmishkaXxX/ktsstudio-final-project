import typing
import redis.asyncio as redis

if typing.TYPE_CHECKING:
    from app.web.app import Application

class Cache:
    def __init__(self, app: "Application") -> None:
        self.app = app
        self.pool: redis.Redis | None = None

    async def connect(self, *args, **kwargs) -> None:
        redis_config = self.app.config.redis
        self.pool = redis.from_url(self.app.config.redis.url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self, *args, **kwargs) -> None:
        if self.pool:
            await self.pool.close()
