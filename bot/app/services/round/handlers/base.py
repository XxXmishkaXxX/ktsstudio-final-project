import typing
from abc import ABC, abstractmethod

from db_core.models.rounds import Round

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseRoundHandler(ABC):
    DEFAULT_SECONDS: int = 30

    def __init__(
        self,
        app: "Application",
        round_: Round,
        game_id: int,
        chat_id: int,
        message_id: int,
    ):
        self.app = app
        self.round_ = round_
        self.game_id = game_id
        self.chat_id = chat_id
        self.message_id = message_id

    # ---- абстрактные коллбеки таймера ----
    @abstractmethod
    async def on_tick(self, sec: int): ...
    @abstractmethod
    async def on_finish(self): ...
    @abstractmethod
    async def on_interrupt(self): ...

    async def start(self):
        """Запускает таймер для текущего состояния."""
        redis_key = f"round:{self.round_.id}:{self.round_.state.value}_timer"
        lock_key = f"{redis_key}:lock"

        await self.app.timer_service.start_timer(
            redis_key=redis_key,
            lock_key=lock_key,
            sec=self.DEFAULT_SECONDS,
            on_tick=self.on_tick,
            on_finish=self.on_finish,
            on_interrupt=self.on_interrupt,
        )
