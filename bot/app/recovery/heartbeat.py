import asyncio
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class HeartbeatService:
    INTERVAL = 3
    TTL = 5

    def __init__(self, app: "Application"):
        self.app = app
        self._tasks = {}

    async def start(self, game_id: int):
        if game_id in self._tasks:
            return

        async def _heartbeat():
            lock_key = f"game:{game_id}:lock"
            while True:
                await self.app.cache.pool.set(lock_key, "1", ex=self.TTL)
                await asyncio.sleep(self.INTERVAL)

        task = asyncio.create_task(_heartbeat())
        self._tasks[game_id] = task

    async def stop(self, game_id: int):
        task = self._tasks.pop(game_id, None)
        if task:
            task.cancel()
        await self.app.cache.pool.delete(f"game:{game_id}:lock")
