import asyncio
import json
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.games.models.rounds import Round, RoundState


class RoundService:
    def __init__(self, app: "Application"):
        self.app = app

    async def get_current_or_create_round(self, game_id: int) -> Round:
        round_ = await self.app.store.rounds.get_current_round(game_id)
        if not round_:
            return await self.app.store.rounds.create_round(
                game_id, round_number=1
            )

        if round_.state in [
            RoundState.faceoff,
            RoundState.buzzer_answer,
            RoundState.team_play,
        ]:
            return round_

        if round_.state == RoundState.finished and round_.round_number + 1 != 3:
            return await self.app.store.rounds.create_round(
                game_id, round_number=round_.round_number + 1
            )
        return None

    async def handle_round(
        self, current_round, game_id, chat_id, message_id, teams=None
    ):
        state = current_round.state
        if state == RoundState.faceoff:
            await self._handle_faceoff(
                current_round, game_id, chat_id, teams, message_id
            )
        elif state == RoundState.buzzer_answer:
            await self._handle_buzzer_answer(
                current_round, game_id, chat_id, message_id
            )
        elif state == RoundState.team_play:
            await self._handle_team_play(
                current_round, game_id, chat_id, message_id
            )
        elif state == RoundState.finished:
            await self.finish_round(current_round.id)

            await self.app.game_service.update_state(
                game_id, chat_id, message_id
            )

    async def _handle_faceoff(
        self, round_, game_id, chat_id, teams, message_id
    ):
        buzzer_ids = await self.choose_buzzers(game_id)
        buzzers = [
            member.user.username or str(member.user_id)
            for team in teams[:2]
            for member in team.members
            if member.user_id in buzzer_ids
        ]
        redis_key = f"round:{round_.id}:buzzer_timer"
        lock_key = f"{redis_key}:lock"

        created = await self.app.cache.pool.set(redis_key, "10", nx=True)
        if not created:
            return

        async def on_tick(sec: int):
            await self.app.renderer.render_in_progress(
                game_id=game_id,
                round_id=round_.id,
                chat_id=chat_id,
                state_r=round_.state.value,
                message_id=message_id,
                round_num=round_.round_number,
                round_question=round_.question.text,
                buzzers=buzzers,
                sec=sec,
            )

        async def on_finish():
            await self.app.cache.pool.delete(redis_key)
            await self.app.cache.pool.delete(lock_key)
            await self.handle_round(round_, game_id, chat_id, message_id, teams)

        async def on_interrupt():
            await self.app.cache.pool.delete(lock_key)
            await self.set_round_state(round_.id, RoundState.buzzer_answer)
            updated_round = await self.app.store.rounds.get_round_by_id(
                round_.id
            )
            await self.handle_round(
                updated_round, game_id, chat_id, message_id, teams
            )

        _ = asyncio.create_task(  # noqa: RUF006
            self.app.timer_service.start_timer(
                redis_key,
                lock_key,
                on_tick=on_tick,
                on_finish=on_finish,
                on_interrupt=on_interrupt,
            )
        )

    async def _handle_buzzer_answer(self, round_, game_id, chat_id, message_id):
        redis_key = f"round:{round_.id}:buzzer_answer_timer"
        lock_key = f"{redis_key}:lock"
        opened_ans = await self.app.store.rounds.get_opened_answers(round_.id)

        created = await self.app.cache.pool.set(redis_key, "30", nx=True)
        if not created:
            return

        async def on_tick(sec: int):
            await self.app.renderer.render_in_progress(
                game_id,
                round_.id,
                chat_id,
                round_.state.value,
                message_id,
                round_num=round_.round_number,
                round_question=round_.question.text,
                player=round_.current_buzzer.username,
                opened_answers=opened_ans,
                sec=sec,
            )

        async def on_finish():
            await self.app.cache.pool.delete(lock_key)
            await self.app.cache.pool.delete(redis_key)
            if not round_.temp_answer:
                await self.set_round_state(round_.id, RoundState.faceoff)
            else:
                await self.set_round_state(round_.id, RoundState.team_play)

            updated_round = await self.app.store.rounds.get_round_by_id(
                round_.id
            )

            await self.handle_round(updated_round, game_id, chat_id, message_id)

        async def on_interrupt():
            await self.app.cache.pool.delete(lock_key)
            updated_round = await self.app.store.rounds.get_round_by_id(
                round_.id
            )
            await self.handle_round(updated_round, game_id, chat_id, message_id)

        _ = asyncio.create_task(  # noqa: RUF006
            self.app.timer_service.start_timer(
                redis_key,
                lock_key,
                on_tick=on_tick,
                on_finish=on_finish,
                on_interrupt=on_interrupt,
            )
        )

    async def _handle_team_play(self, round_, game_id, chat_id, message_id):
        redis_key = f"round:{round_.id}:teamplay_timer"
        lock_key = f"{redis_key}:lock"

        created = await self.app.cache.pool.set(redis_key, "60", nx=True)
        if not created:
            return

        opened_ans_db = await self.app.store.rounds.get_opened_answers(
            round_.id
        )
        opened_ans_data = [
            {
                "position": ans.answer_option.position,
                "text": ans.answer_option.text,
                "points": ans.answer_option.points,
            }
            for ans in opened_ans_db
        ]

        await self.app.cache.pool.set(
            f"round:{round_.id}:opened_answers",
            json.dumps(opened_ans_data),
        )

        async def on_tick(sec: int):
            count_strikes = await self.app.cache.pool.get(
                f"round:{round_.id}:team:{round_.current_team_id}:strikes"
            )
            opened_ans_json = await self.app.cache.pool.get(
                f"round:{round_.id}:opened_answers"
            )
            opened_ans = json.loads(opened_ans_json) if opened_ans_json else []
            score = await self.app.cache.pool.get(f"round:{round_.id}:score")

            await self.app.renderer.render_in_progress(
                game_id,
                round_.id,
                chat_id,
                round_.state.value,
                message_id,
                round_num=round_.round_number,
                round_question=round_.question.text,
                score=int(score) if score else 0,
                team=round_.current_team,
                count_strikes=int(count_strikes) if count_strikes else 0,
                opened_answers=opened_ans,
                sec=sec,
            )

        async def on_finish():
            await self.switch_team(round_)
            await self.app.cache.pool.delete(redis_key)
            await self.app.cache.pool.delete(lock_key)
            updated_round = await self.app.store.rounds.get_round_by_id(
                round_.id
            )
            await self.handle_round(updated_round, game_id, chat_id, message_id)

        async def on_interrupt():
            strikes = await self.app.cache.pool.get(
                f"round:{round_.id}:team:{round_.current_team_id}:strikes"
            )
            self.app.logger.info(strikes)
            if int(strikes or 0) >= 3:
                await self.switch_team(round_)
            else:
                await self.set_round_state(round_.id, RoundState.finished)
            updated_round = await self.app.store.rounds.get_round_by_id(
                round_.id
            )
            await self.app.cache.pool.delete(lock_key)
            await self.handle_round(updated_round, game_id, chat_id, message_id)

        _ = asyncio.create_task(  # noqa: RUF006
            self.app.timer_service.start_timer(
                redis_key,
                lock_key,
                on_tick=on_tick,
                on_finish=on_finish,
                on_interrupt=on_interrupt,
            )
        )

    async def choose_buzzers(self, game_id: int) -> list[int]:
        teams = await self.app.store.teams.get_game_teams(game_id)
        if len(teams) < 2:
            raise Exception("Недостаточно команд для faceoff")

        team1, team2 = teams[0], teams[1]
        max_players = 5

        key_idx = f"game:{game_id}:buzzer_idx"
        data = await self.app.cache.pool.get(key_idx)
        if data:
            obj = json.loads(data)
            idx1, idx2 = obj["idx1"], obj["idx2"]
        else:
            idx1, idx2 = 0, 0

        player1 = team1.members[idx1 % max_players].user_id
        player2 = team2.members[idx2 % max_players].user_id

        # сохраняем новых баззеров отдельно
        key_faceoff = f"game:{game_id}:faceoff_players"
        await self.app.cache.pool.set(
            key_faceoff, json.dumps({"p1": player1, "p2": player2})
        )

        # обновляем индексы на следующий раз
        await self.app.cache.pool.set(
            key_idx,
            json.dumps(
                {
                    "idx1": (idx1 + 1) % max_players,
                    "idx2": (idx2 + 1) % max_players,
                }
            ),
        )

        return [player1, player2]

    async def get_current_buzzers(self, game_id: int) -> list[int]:
        key_faceoff = f"game:{game_id}:faceoff_players"
        data = await self.app.cache.pool.get(key_faceoff)
        if not data:
            return []
        obj = json.loads(data)
        return [obj["p1"], obj["p2"]]

    async def register_buzzer(self, round_id: int, user_id: int) -> bool:
        round_ = await self.app.store.rounds.get_round_by_id(round_id)
        if not round_:
            raise Exception("Раунд не найден")

        allowed = await self.get_current_buzzers(round_.game_id)
        if user_id not in allowed:
            raise Exception("Вы не участвуете в faceoff")

        round_ = await self.app.store.rounds.set_buzzer(round_id, user_id)

        await self.app.cache.pool.delete(f"round:{round_id}:buzzer_timer")

        return True

    async def set_round_state(self, round_id: int, state: RoundState):
        return await self.app.store.rounds.set_round_state(round_id, state)

    async def finish_round(self, round_id: int):
        round_ = await self.app.store.rounds.get_round_by_id(round_id)
        if not round_:
            return

        round_.current_buzzer_id = None
        round_.current_team_id = None
        await self.app.store.rounds.update_round(round_)

        redis = self.app.cache.pool
        keys_pattern = f"round:{round_id}:*"

        cursor = b"0"
        while cursor:
            cursor, keys = await redis.scan(
                cursor=cursor, match=keys_pattern, count=100
            )
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break

    async def check_answer(self, round_id: int, answer: str) -> dict:
        round_ = await self.app.store.rounds.get_round_by_id(round_id)
        question = round_.question
        answers = question.answers
        total_answers = len(answers)

        ans_obj = next(
            (a for a in answers if a.text.lower() == answer.lower()), None
        )
        if not ans_obj:
            return {"found": False}

        added = await self.app.store.rounds.add_opened_answer_if_not_exists(
            round_id, ans_obj.id
        )
        if not added:
            return {"found": False, "reason": "already_opened"}

        opened_count = await self.app.store.rounds.count_opened_answers(
            round_id
        )
        all_opened = opened_count == total_answers

        sorted_answers = sorted(answers, key=lambda a: a.points, reverse=True)
        rank = next(
            idx for idx, a in enumerate(sorted_answers) if a.id == ans_obj.id
        )

        return {
            "found": True,
            "rank": rank,
            "score": ans_obj.points,
            "all_opened": all_opened,
        }

    async def add_score(self, round_id: int, score: int):
        await self.app.store.rounds.add_score(round_id, score)

        score = await self.app.store.rounds.get_score(round_id)
        await self.app.cache.pool.set(f"round:{round_id}:score", score)

    async def add_strike(self, round_id: int, team_id: int):
        key = f"round:{round_id}:team:{team_id}:strikes"
        return await self.app.cache.pool.incr(key)

    async def switch_team(self, round_: Round):
        if not round_.current_team_id:
            return None

        teams_in_game = await self.app.store.teams.get_game_teams(
            round_.game_id
        )
        if len(teams_in_game) < 2:
            return round_.current_team_id

        current_idx = 0 if round_.current_team_id == teams_in_game[0].id else 1
        next_idx = 1 - current_idx

        round_.current_team_id = teams_in_game[next_idx].id
        await self.app.store.rounds.update_round(round_)

        await self.app.cache.pool.set(
            f"round:{round_.id}:team:{round_.current_team_id}:strikes", 0
        )

        return round_.current_team_id

    async def buzzer_answer_question(
        self, game_id: int, user_id: int, ans: str
    ):
        round_ = await self.app.store.rounds.get_current_round(game_id)
        buzzer_id = round_.current_buzzer_id
        if user_id != buzzer_id:
            return

        res = await self.check_answer(round_.id, ans)
        buzzers = await self.get_current_buzzers(game_id)

        if res["found"] and res["rank"] == 0:
            team_id = await self.app.store.teams.get_team_by_user_id(
                game_id, user_id
            )
            round_.current_team_id = team_id
            await self.set_round_state(round_.id, RoundState.team_play)
            await self.add_score(round_.id, res["score"])

        elif round_.temp_answer:
            first = round_.temp_answer
            if res["found"] and (
                not first["found"] or res["rank"] < first.get("rank", 999)
            ):
                team_id = await self.app.store.teams.get_team_by_user_id(
                    game_id, user_id
                )
                await self.add_score(round_.id, res["score"])
            elif first["found"]:
                team_id = await self.app.store.teams.get_team_by_user_id(
                    game_id,
                    buzzers[0] if buzzers[0] != user_id else buzzers[1],
                )
            else:
                team_id = None

            if team_id:
                round_.current_team_id = team_id
                await self.set_round_state(round_.id, RoundState.team_play)
        else:
            round_.temp_answer = res if res["found"] else {"found": False}
            team_id = await self.app.store.teams.get_team_by_user_id(
                game_id, user_id
            )
            round_.current_team_id = team_id
            next_buzzer = next((b for b in buzzers if b != user_id), None)
            await self.app.store.rounds.overwrite_buzzer(round_.id, next_buzzer)
            if res["found"]:
                await self.add_score(round_.id, res["score"])

        await self.app.cache.pool.delete(
            f"round:{round_.id}:buzzer_answer_timer"
        )
        await self.app.store.rounds.update_round(round_)

    async def team_answer_question(
        self, game_id: int, chat_id: int, user_id: int, ans: str
    ):
        round_ = await self.app.store.rounds.get_current_round(game_id)

        user_in_team = any(
            member.user_id == user_id for member in round_.current_team.members
        )
        if not user_in_team:
            return

        res = await self.check_answer(round_.id, ans)

        if not res["found"] and res.get("reason"):
            return

        if res["found"]:
            await self.add_score(round_.id, res["score"])

            opened_answers = await self.app.store.rounds.get_opened_answers(
                round_.id
            )
            opened_answers_data = [
                {
                    "position": ans.answer_option.position,
                    "text": ans.answer_option.text,
                    "points": ans.answer_option.points,
                }
                for ans in opened_answers
            ]

            await self.app.cache.pool.set(
                f"round:{round_.id}:opened_answers",
                json.dumps(opened_answers_data),
            )

        elif not res["found"]:
            await self.add_strike(round_.id, round_.current_team.id)

        await self.app.store.rounds.update_round(round_)

        count_strikes = await self.app.cache.pool.get(
            f"round:{round_.id}:team:{round_.current_team_id}:strikes"
        )
        count_strikes = int(count_strikes or 0)

        score = await self.app.cache.pool.get(f"round:{round_.id}:score")
        score = int(score or 0)

        opened_ans_json = await self.app.cache.pool.get(
            f"round:{round_.id}:opened_answers"
        )
        opened_ans = json.loads(opened_ans_json) if opened_ans_json else []

        sec = await self.app.cache.pool.get(f"round:{round_.id}:teamplay_timer")
        sec = int(sec or 0)

        message_id = await self.app.cache.pool.get(f"game:{game_id}:message_id")

        await self.app.renderer.render_in_progress(
            game_id=game_id,
            round_id=round_.id,
            chat_id=chat_id,
            state_r=round_.state.value,
            message_id=message_id,
            round_num=round_.round_number,
            round_question=round_.question.text,
            score=score,
            team=round_.current_team,
            count_strikes=count_strikes,
            opened_answers=opened_ans,
            sec=sec,
        )
        if count_strikes >= 3:
            await self.app.cache.pool.delete(
                f"round:{round_.id}:teamplay_timer"
            )
            return

        if res.get("all_opened"):
            final_score = await self.app.store.rounds.get_score(round_.id)
            await self.app.store.teams.add_team_score(
                round_.current_team.id, final_score
            )
            await self.set_round_state(round_.id, RoundState.finished)
            await self.app.cache.pool.delete(
                f"round:{round_.id}:teamplay_timer"
            )
