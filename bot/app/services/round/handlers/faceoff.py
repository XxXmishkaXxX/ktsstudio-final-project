import typing

from db_core.models.rounds import Round, RoundState

from .base import BaseRoundHandler

if typing.TYPE_CHECKING:
    from app.web.app import Application


class FaceoffHandler(BaseRoundHandler):
    DEFAULT_SECONDS = 10

    def __init__(
        self,
        app: "Application",
        round_: Round,
        game_id: int,
        chat_id: int,
        message_id: int,
    ):
        super().__init__(app, round_, game_id, chat_id, message_id)
        self.buzzers: list[str] | None = None

    async def on_tick(self, sec: int):
        await self.app.renderer.render_in_progress(
            game_id=self.game_id,
            round_id=self.round_.id,
            chat_id=self.chat_id,
            state_r=self.round_.state.value,
            message_id=self.message_id,
            round_num=self.round_.round_number,
            round_question=self.round_.question.text,
            buzzers=self.buzzers,
            sec=sec,
        )

    async def on_finish(
        self,
    ):
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer"
        )
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
        )
        await self.app.round_service.handle_round(
            self.round_, self.game_id, self.chat_id, self.message_id
        )

    async def on_interrupt(
        self,
    ):
        await self.app.cache.pool.delete(
            f"round:{self.round_.id}:{self.round_.state.value}_timer:lock"
        )

        await self.app.store.rounds.set_round_state(
            self.round_.id, RoundState.buzzer_answer
        )
        updated_round = await self.app.store.rounds.get_round_by_id(
            self.round_.id
        )
        await self.app.round_service.handle_round(
            updated_round, self.game_id, self.chat_id, self.message_id
        )

    async def start(self):
        teams = await self.app.store.teams.get_game_teams(self.game_id)
        buzzer_ids = await self.app.round_service.choose_buzzers(self.game_id)
        self.buzzers = [
            member.user.username or str(member.user_id)
            for team in teams
            for member in team.members
            if member.user_id in buzzer_ids
        ]

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
