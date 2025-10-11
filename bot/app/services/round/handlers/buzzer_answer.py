from .base import BaseRoundHandler
import typing
from db_core.models.rounds import Round, RoundAnswer, RoundState

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BuzzerAnswerHandler(BaseRoundHandler):
    DEFAULT_SECONDS = 30

    def __init__(
        self,
        app: "Application",
        round_: Round,
        game_id: int,
        chat_id: int,
        message_id: int,
    ):
        super().__init__(app, round_, game_id, chat_id, message_id)
        self.opened_ans: list[RoundAnswer] | None = None

    async def on_tick(self, sec: int):
        await self.app.renderer.render_in_progress(
            game_id=self.game_id,
            round_id=self.round_.id,
            chat_id=self.chat_id,
            state_r=self.round_.state.value,
            message_id=self.message_id,
            round_num=self.round_.round_number,
            round_question=self.round_.question.text,
            player=self.round_.current_buzzer.username,
            opened_answers=self.opened_ans,
            sec=sec,
        )

    async def on_finish(self):
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer"
        )
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
        )
        if not self.round_.temp_answer:
            next_state = RoundState.faceoff
        else:
            next_state = RoundState.team_play

        await self.app.store.rounds.set_round_state(self.round_.id, next_state)
        await self.app.store.rounds.overwrite_buzzer(self.round_.id, None)

        updated_round = await self.app.store.rounds.get_round_by_id(
            self.round_.id
        )
        await self.app.round_service.handle_round(
            updated_round, self.game_id, self.chat_id, self.message_id
        )

    async def on_interrupt(self):
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
        )
        updated_round = await self.app.store.rounds.get_round_by_id(
            self.round_.id
        )
        await self.app.round_service.handle_round(
            updated_round, self.game_id, self.chat_id, self.message_id
        )

    async def start(self):
        self.opened_ans = await self.app.store.rounds.get_opened_answers(
            self.round_.id
        )

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
