import json
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.bot.keyboards import buzzer_button, join_game, leave_game
from app.bot.texts import (
    get_finish_game_text,
    get_game_created_text,
    get_game_round_buzzers_text,
    get_game_round_teamplay_text,
)


class GameRenderer:
    def __init__(self, app: "Application"):
        self.app = app

    def _get_members(self, team):
        return [m.user.username or str(m.user_id) for m in team.members]

    def _build_join_leave_kb(self, game_id: int, team1, team2):
        has_players = bool(team1.members or team2.members)
        kb = {"inline_keyboard": []}
        jg = join_game(game_id, team1.id, team2.id)

        if len(team1.members) < 5:
            kb["inline_keyboard"].append(jg["inline_keyboard"][0])
        if len(team2.members) < 5:
            kb["inline_keyboard"].append(jg["inline_keyboard"][1])
        if has_players:
            kb["inline_keyboard"].extend(leave_game(game_id)["inline_keyboard"])

        return kb

    async def render_created(
        self, game_id: int, chat_id: int, teams, message_id: int | None = None
    ):
        if len(teams) < 2:
            raise Exception("Недостаточно команд для отображения игры")

        team1, team2 = teams[0], teams[1]
        members_team1 = self._get_members(team1)
        members_team2 = self._get_members(team2)

        text = get_game_created_text(team_1=members_team1, team_2=members_team2)
        kb = self._build_join_leave_kb(game_id, team1, team2)

        if message_id:
            await self.app.telegram.edit_message(
                chat_id,
                message_id,
                text,
                reply_markup=json.dumps(kb),
                parse_mode="HTML",
            )
        else:
            response = await self.app.telegram.send_message(
                chat_id, text, reply_markup=json.dumps(kb), parse_mode="HTML"
            )
            await self.app.cache.pool.set(
                f"game:{game_id}:message_id", response["result"]["message_id"]
            )

    async def render_starting(
        self,
        game_id: int,
        chat_id: int,
        message_id: int,
        teams,
        sec: int,
    ):
        team1, team2 = teams[0], teams[1]
        members_team1 = self._get_members(team1)
        members_team2 = self._get_members(team2)

        text = get_game_created_text(
            team_1=members_team1,
            team_2=members_team2,
            extra=f"Игра начнется через {sec} сек.",
        )
        kb = self._build_join_leave_kb(game_id, team1, team2)

        await self.app.telegram.edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=json.dumps(kb),
            parse_mode="HTML",
        )

    async def render_in_progress(
        self,
        game_id: int,
        round_id: int,
        chat_id: int,
        state_r: str,
        message_id: int,
        **text_kwargs: dict,
    ):
        kb = {}
        match state_r:
            case "faceoff":
                text = get_game_round_buzzers_text(**text_kwargs)
                kb = buzzer_button(game_id, round_id)
            case "buzzer_answer":
                text = get_game_round_buzzers_text(**text_kwargs)
            case "team_play":
                text = get_game_round_teamplay_text(**text_kwargs)

        await self.app.telegram.edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=json.dumps(kb) if kb else {},
            parse_mode="HTML",
        )

    async def render_finished(
        self, chat_id: int, message_id: int, **text_kwargs
    ):
        text = get_finish_game_text(**text_kwargs)
        await self.app.telegram.edit_message(
            chat_id, message_id, text, parse_mode="HTML"
        )
