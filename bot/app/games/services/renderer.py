import json
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.bot.keyboards import buzzer_button, join_game
from app.bot.texts import (
    get_finish_game_text,
    get_game_created_text,
    get_game_round_buzzers_text,
    get_game_round_teamplay_text,
)


class GameRenderer:
    def __init__(self, app: "Application"):
        self.app = app

    async def render_created(
        self, game_id: int, chat_id: int, teams, message_id: int | None = None
    ):
        if len(teams) < 2:
            raise Exception("Недостаточно команд для отображения игры")

        team1, team2 = teams[0], teams[1]

        members_team1 = [
            m.user.username or str(m.user_id) for m in team1.members
        ]
        members_team2 = [
            m.user.username or str(m.user_id) for m in team2.members
        ]

        text = get_game_created_text(
            team_1=members_team1,
            team_2=members_team2,
        )

        kb = json.dumps(join_game(game_id, team1.id, team2.id))
        if message_id:
            await self.app.telegram.edit_message(
                chat_id, message_id, text, reply_markup=kb, parse_mode="HTML"
            )
        else:
            response = await self.app.telegram.send_message(
                chat_id, text, reply_markup=kb, parse_mode="HTML"
            )
            await self.app.cache.pool.set(
                f"game:{game_id}:message_id", response["result"]["message_id"]
            )

    async def render_starting(
        self,
        chat_id: int,
        message_id: int,
        team_1: list[str],
        team_2: list[str],
        sec: int,
    ):
        text = get_game_created_text(
            team_1=team_1,
            team_2=team_2,
            extra=f"Игра начнется через {sec} сек.",
        )
        await self.app.telegram.edit_message(
            chat_id, message_id, text, parse_mode="HTML"
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

        if state_r == "faceoff":
            text = get_game_round_buzzers_text(**text_kwargs)
            kb = buzzer_button(game_id, round_id)
        elif state_r == "buzzer_answer":
            text = get_game_round_buzzers_text(**text_kwargs)
        elif state_r == "team_play":
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
