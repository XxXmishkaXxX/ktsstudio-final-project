import asyncio
import typing
import uuid

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TimerService:
    def __init__(self, app: "Application"):
        self.app = app

    async def _release_lock(self, redis, lock_key: str, token: str):
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            await redis.eval(lua, keys=[lock_key], args=[token])
        except Exception:
            self.app.logger.debug(
                "Failed to release lock via eval for %s", lock_key
            )

    async def _handle_interrupt(
        self,
        redis,
        redis_key: str,
        on_interrupt: typing.Callable[[], typing.Awaitable[None]],
    ):
        await redis.delete(redis_key)
        await on_interrupt()

    async def _tick(
        self,
        redis,
        redis_key: str,
        lock_key: str,
        on_tick: typing.Callable[[int], typing.Awaitable[None]],
        on_finish: typing.Callable[[], typing.Awaitable[None]],
        on_interrupt: typing.Callable[[], typing.Awaitable[None]],
    ):
        counter = 0
        while True:
            raw = await redis.get(redis_key)
            if raw is None:
                await on_interrupt()
                return

            try:
                sec = int(raw)
            except (TypeError, ValueError):
                await self._handle_interrupt(redis, redis_key, on_interrupt)
                return

            if sec <= 0:
                await self._handle_interrupt(redis, redis_key, on_finish)
                return

            if counter % 5 == 0:
                try:
                    await on_tick(sec)
                except Exception:
                    self.app.logger.exception("Error in start_timer")
            counter += 1

            await redis.decr(redis_key)
            await redis.expire(lock_key, 15)
            await asyncio.sleep(1)

    async def start_timer(
        self,
        redis_key: str,
        lock_key: str,
        on_tick: typing.Callable[[int], typing.Awaitable[None]],
        on_finish: typing.Callable[[], typing.Awaitable[None]],
        on_interrupt: typing.Callable[
            [], typing.Awaitable[None]
        ] = lambda: None,
    ):
        redis = self.app.cache.pool
        token = uuid.uuid4().hex

        got = await redis.set(lock_key, token, nx=True, ex=15)
        if not got:
            self.app.logger.info("Another worker handles timer %s", redis_key)
            return

        try:
            await self._tick(
                redis, redis_key, lock_key, on_tick, on_finish, on_interrupt
            )
        except Exception:
            self.app.logger.exception(
                "Error in redis timer loop for %s", redis_key
            )
            try:
                await redis.delete(redis_key)
            except Exception:
                pass
        finally:
            await self._release_lock(redis, lock_key, token)
