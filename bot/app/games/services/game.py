import asyncio
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.games.models.games import GameState
from app.users.models import State as UserState


class GameService:
    def __init__(self, app: "Application"):
        self.app = app

    # ----------------- public API -----------------

    async def create_game(self, chat_id: int, tg_id: int):
        game = await self.app.store.games.create_game(chat_id)
        for _ in range(2):
            await self.app.store.teams.create_team(game.id)

        await self.app.cache.pool.set(f"game:{game.id}:user:started", tg_id)
        self.app.logger.info("Create game")
        await self.update_state(game.id, chat_id)

    async def stop_game(self, game_id: int, chat_id: int):
        await self.app.store.games.set_game_state(game_id, GameState.finished)
        round_id = await self.app.store.games.get_current_round_id(game_id)
        if round_id:
            await self.app.round_service.finish_round(round_id)
        message_id = int(
            await self.app.cache.pool.get(f"game:{game_id}:message_id")
        )
        await self.update_state(game_id, chat_id, message_id)

    async def join_to_game(
        self,
        game_id: int,
        team_id: int,
        tg_id: int,
        chat_id: int,
        message_id: int | None = None,
    ):
        teams = await self.app.store.teams.get_game_teams(game_id)

        if not teams:
            raise Exception(
                "К игре, к которой вы хотите присоединиться, нет команд"
            )

        current_team = None
        for team in teams:
            for member in team.members:
                if member.user_id == tg_id:
                    current_team = team
                    break
            if current_team:
                break

        if current_team and current_team.id == team_id:
            raise Exception("Вы уже находитесь в этой команде")

        new_team = next((t for t in teams if t.id == team_id), None)
        if not new_team:
            raise Exception("Команда не найдена")

        if len(new_team.members) >= 5:
            raise Exception("В команде нет свободных мест")

        if current_team:
            await self.app.store.teams.leave_team(current_team.id, tg_id)

        await self.app.store.teams.join_team(new_team.id, tg_id)
        await self.update_state(game_id, chat_id, message_id)
        return new_team.id

    async def update_state(
        self, game_id: int, chat_id: int, message_id: int | None = None
    ):
        state = await self.app.store.games.get_game_state(game_id)
        handler_map = {
            GameState.created: self._handle_created,
            GameState.starting: self._handle_starting,
            GameState.in_progress: self._handle_in_progress,
            GameState.finished: self._handle_finished,
        }

        handler = handler_map.get(state)
        if handler:
            await handler(game_id, chat_id, message_id)

    # ----------------- handlers for each game state -----------------

    async def _handle_created(self, game_id, chat_id, message_id):
        teams = await self.app.store.teams.get_game_teams(game_id)

        ready = all(len(t.members) == 5 for t in teams[:2])
        if ready:
            await self.app.store.games.set_game_state(
                game_id, GameState.starting
            )
            await self.update_state(game_id, chat_id, message_id)
        else:
            await self.app.renderer.render_created(
                game_id, chat_id, teams, message_id
            )

    async def _handle_starting(self, game_id, chat_id, message_id):
        redis_key = f"game:{game_id}:timer"
        lock_key = f"{redis_key}:lock"

        await self.app.heartbeat.start(game_id)

        teams = await self.app.store.teams.get_game_teams(game_id)
        team_1 = [m.user.username or str(m.user_id) for m in teams[0].members]
        team_2 = [m.user.username or str(m.user_id) for m in teams[1].members]

        async def on_tick(sec: int):
            await self.app.renderer.render_starting(
                chat_id,
                message_id,
                team_1=team_1,
                team_2=team_2,
                sec=sec,
            )

        async def on_finish():
            teams_now = await self.app.store.teams.get_game_teams(game_id)
            ready_now = all(len(t.members) == 5 for t in teams_now[:2])
            if ready_now:
                await self.app.store.games.set_game_state(
                    game_id, GameState.in_progress
                )
            else:
                await self.app.store.games.set_game_state(
                    game_id, GameState.created
                )
            await self.app.cache.pool.delete(redis_key)
            await self.app.cache.pool.delete(lock_key)
            await self.update_state(game_id, chat_id, message_id)

        async def on_interrupt():
            await self.app.store.games.set_game_state(
                game_id, GameState.created
            )
            await self.app.renderer.render_created(
                game_id, chat_id, message_id, teams
            )

        _ = asyncio.create_task(  # noqa: RUF006
            self.app.timer_service.start_timer(
                redis_key,
                lock_key,
                sec=5,
                on_tick=on_tick,
                on_finish=on_finish,
                on_interrupt=on_interrupt,
            )
        )

    async def _handle_in_progress(self, game_id, chat_id, message_id):
        current_round = (
            await self.app.round_service.get_current_or_create_round(game_id)
        )
        if not current_round:
            await self.app.store.games.set_game_state(
                game_id, GameState.finished
            )
            await self.update_state(game_id, chat_id, message_id)
            return

        if current_round.round_number != 1:
            response = await self.app.telegram.send_message(
                chat_id,
                f"Раунд {current_round.round_number}",
                parse_mode="HTML",
            )
            message_id = response["result"]["message_id"]
            await self.app.cache.pool.set(
                f"game:{game_id}:message_id", message_id
            )

        await self.app.round_service.handle_round(
            current_round, game_id, chat_id, message_id
        )

    async def _handle_finished(self, game_id, chat_id, message_id):
        team1, team2 = await self.app.store.teams.get_game_teams(game_id)

        if team1.score > team2.score:
            winners, score = (
                [member.user.username for member in team1.members],
                team1.score,
            )
        elif team2.score > team1.score:
            winners, score = (
                [member.user.username for member in team2.members],
                team1.score,
            )
        else:
            winners, score = None, None

        for team in (team1, team2):
            for member in team.members:
                await self.app.store.users.set_state_user(
                    member.user_id, UserState.idle
                )

        await self.app.heartbeat.stop(game_id)
        await self.app.renderer.render_finished(
            chat_id, message_id, winners=winners, score=score
        )

    # ----------------- utils и входящие ответы -----------------

    async def get_user_created_game(self, game_id: int):
        user_id = await self.app.cache.pool.get(f"game:{game_id}:user:started")
        return int(user_id)
