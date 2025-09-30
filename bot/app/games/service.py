import json
import typing

from app.bot.keyboards import join_game
from app.bot.texts import get_game_text
from app.games.models.games import GameState

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_game(self, chat_id: int):
        game = await self.app.store.games.create_game(chat_id)
        for _ in range(2):
            await self.app.store.teams.create_team(game.id)

        await self.render_game(game.id, chat_id)

    async def join_to_game(
        self,
        game_id: int,
        team_id: int,
        tg_id: int,
        chat_id: int,
        message_id: int,
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
        await self.render_game(game_id, chat_id, message_id)
        return True

    async def render_game(
        self, game_id: int, chat_id: int, message_id: int | None = None
    ):
        state = await self.app.store.games.get_game_state(game_id)

        if state == GameState.created:
            await self._render_created(game_id, chat_id, message_id)

        elif state == GameState.running:
            await self._render_running(game_id, chat_id, message_id)

        elif state == GameState.finished:
            await self._render_finished(game_id, chat_id, message_id)

        else:
            # fallback — если появятся новые стейты
            await self._render_default(game_id, chat_id, message_id, state)

    async def _render_created(
        self, game_id: int, chat_id: int, message_id: int | None
    ):
        teams = await self.app.store.teams.get_game_teams(game_id)

        if len(teams) < 2:
            raise Exception("Недостаточно команд для отображения игры")

        team1, team2 = teams[0], teams[1]

        members_team1 = [
            m.user.username or str(m.user_id) for m in team1.members
        ]
        members_team2 = [
            m.user.username or str(m.user_id) for m in team2.members
        ]

        text = get_game_text(
            team_1=members_team1,
            team_2=members_team2,
            state=GameState.created.value,
        )

        if message_id:
            await self.app.telegram.edit_message(
                chat_id,
                message_id,
                text,
                reply_markup=json.dumps(join_game(game_id, team1.id, team2.id)),
                parse_mode="HTML",
            )
        else:
            await self.app.telegram.send_message(
                chat_id,
                text,
                reply_markup=json.dumps(join_game(game_id, team1.id, team2.id)),
                parse_mode="HTML",
            )

    async def _render_running(
        self, game_id: int, chat_id: int, message_id: int | None
    ):
        text = get_game_text(team1=[], team2=[], state=GameState.running)
        await self.app.telegram.send_message(chat_id, text, parse_mode="HTML")

    async def _render_finished(
        self, game_id: int, chat_id: int, message_id: int | None
    ):
        text = get_game_text(team1=[], team2=[], state=GameState.finished)
        await self.app.telegram.send_message(chat_id, text, parse_mode="HTML")

    async def _render_default(
        self,
        game_id: int,
        chat_id: int,
        message_id: int | None,
        state: GameState,
    ):
        text = get_game_text(team1=[], team2=[], state=state)
        await self.app.telegram.send_message(chat_id, text, parse_mode="HTML")
