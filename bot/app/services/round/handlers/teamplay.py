import json
from .base import BaseRoundHandler
import typing
from db_core.models.rounds import Round, RoundState

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TeamPlayHandler(BaseRoundHandler):
    DEFAULT_SECONDS = 60

    def __init__(
        self,
        app: "Application",
        round_: Round,
        game_id: int,
        chat_id: int,
        message_id: int,
    ):
        super().__init__(app, round_, game_id, chat_id, message_id)

    async def on_tick(self, sec: int):
        opened_ans_json = await self.app.cache.pool.get(
            f"round:{self.round_.id}:opened_answers"
        )
        opened_ans = json.loads(opened_ans_json) if opened_ans_json else []


        count_strikes = await self.app.cache.pool.get(
            f"round:{self.round_.id}:team:{self.round_.current_team_id}:strikes",
        )
        score = await self.app.store.rounds.get_score(self.round_.id)

        await self.app.renderer.render_in_progress(
            self.game_id,
            self.round_.id,
            self.chat_id,
            self.round_.state.value,
            self.message_id,
            round_num=self.round_.round_number,
            round_question=self.round_.question.text,
            score=score,
            team=self.round_.current_team,
            count_strikes=int(count_strikes) if count_strikes else 0,
            opened_answers=opened_ans,
            sec=sec,
        )

    async def on_finish(self):
        await self.app.round_service.switch_team(self.round_)
        updated_round = await self.app.store.rounds.get_round_by_id(
            self.round_.id
        )
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer"
        )
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
        )
        await self.app.round_service.handle_round(
            updated_round, self.game_id, self.chat_id, self.message_id
        )

    async def on_interrupt(self):
        count_strikes = await self.app.cache.pool.get(
            f"round:{self.round_.id}:team:{self.round_.current_team_id}:strikes",
        )
        if int(count_strikes or 0) >= 3:
            await self.app.round_service.switch_team(self.round_)
        else:
            await self.app.store.rounds.set_round_state(
                self.round_.id, RoundState.finished
            )
        updated_round = await self.app.store.rounds.get_round_by_id(
            self.round_.id
        )
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
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
