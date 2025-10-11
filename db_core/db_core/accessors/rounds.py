import random

from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from db_core.models.games import Game
from db_core.models.questions import Question
from db_core.models.rounds import Round, RoundAnswer, RoundState
from db_core.models.teams import Team, TeamMember

from .base import BaseAccessor


class RoundAccessor(BaseAccessor):
    async def create_round(self, game_id: int, round_number: int) -> Round:
        async with self.app.database.session() as session:
            questions = (
                (
                    await session.execute(
                        select(Question).options(selectinload(Question.answers))
                    )
                )
                .scalars()
                .all()
            )

            if not questions:
                raise ValueError("Нет доступных вопросов")

            question = random.choice(questions)

            round_obj = Round(
                game_id=game_id,
                round_number=round_number,
                question_id=question.id,
            )
            session.add(round_obj)
            await session.commit()
            await session.refresh(round_obj)

            game = await session.get(Game, game_id)
            game.current_round_id = round_obj.id
            await session.commit()

            round_obj.question = question
            return round_obj

    async def get_current_round(self, game_id: int) -> Round | None:
        async with self.app.database.session() as session:
            q = await session.execute(
                select(Round)
                .options(
                    selectinload(Round.question).selectinload(Question.answers),
                    selectinload(Round.current_buzzer),
                    selectinload(Round.current_team)
                    .selectinload(Team.members)
                    .selectinload(TeamMember.user),
                )
                .where(Round.game_id == game_id)
                .order_by(Round.round_number.desc())
                .limit(1)
            )
            return q.scalar_one_or_none()

    async def get_round_by_id(self, round_id: int) -> Round | None:
        async with self.app.database.session() as session:
            q = await session.execute(
                select(Round)
                .options(
                    selectinload(Round.question).selectinload(Question.answers),
                    selectinload(Round.current_buzzer),
                    selectinload(Round.current_team)
                    .selectinload(Team.members)
                    .selectinload(TeamMember.user),
                )
                .where(Round.id == round_id)
            )
            return q.scalar_one_or_none()

    async def update_round(self, round_: Round) -> Round:
        async with self.app.database.session() as session:
            session.add(round_)
            await session.commit()
            await session.refresh(round_)
            return round_

    async def set_round_state(self, round_id: int, state: RoundState) -> Round:
        async with self.app.database.session() as session:
            q = await session.execute(select(Round).where(Round.id == round_id))
            round_ = q.scalar_one()
            round_.state = state
            await session.commit()
            await session.refresh(round_)
            return round_

    async def get_round_state(self, round_id: int) -> Round:
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Round.state).where(Round.id == round_id)
                )
            ).scalar_one_or_none()

    async def set_buzzer(self, round_id: int, user_id: int) -> Round:
        async with self.app.database.session() as session:
            result = await session.execute(
                update(Round)
                .where(Round.id == round_id, Round.current_buzzer_id.is_(None))
                .values(current_buzzer_id=user_id)
                .returning(Round)
            )
            updated_round = result.scalar_one_or_none()

            if not updated_round:
                raise Exception("Кто-то уже нажал кнопку")

            await session.commit()

    async def overwrite_buzzer(self, round_id: int, user_id: int) -> Round:
        async with self.app.database.session() as session:
            result = await session.execute(
                update(Round)
                .where(Round.id == round_id)
                .values(current_buzzer_id=user_id)
                .returning(Round)
            )
            updated_round = result.scalar_one_or_none()
            if not updated_round:
                raise Exception("Раунд не найден")

            await session.commit()
            await session.refresh(updated_round)
            return updated_round

    async def add_opened_answer_if_not_exists(
        self, round_id: int, answer_id: int
    ) -> bool:
        async with self.app.database.session() as session:
            existing = await session.execute(
                select(RoundAnswer).where(
                    RoundAnswer.round_id == round_id,
                    RoundAnswer.answer_option_id == answer_id,
                )
            )
            if existing.scalar_one_or_none():
                return False

            round_answer = RoundAnswer(
                round_id=round_id,
                answer_option_id=answer_id,
            )
            session.add(round_answer)
            await session.commit()
            return True

    async def get_opened_answers(self, round_id: int) -> list[dict]:
        async with self.app.database.session() as session:
            q = await session.execute(
                select(RoundAnswer)
                .options(selectinload(RoundAnswer.answer_option))
                .where(RoundAnswer.round_id == round_id)
            )

            return [
                {
                    "position": ans.answer_option.position,
                    "text": ans.answer_option.text,
                    "points": ans.answer_option.points,
                }
                for ans in q.scalars().all()
            ]

    async def count_opened_answers(self, round_id: int) -> int:
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(func.count())
                    .select_from(RoundAnswer)
                    .where(RoundAnswer.round_id == round_id)
                )
            ).scalar_one()

    async def add_score(self, round_id: int, score: int) -> int:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Round).where(Round.id == round_id)
            )
            round_ = result.scalar_one_or_none()

            if not round_:
                raise ValueError("Раунд не найден")

            update_stmt = (
                update(Round)
                .where(Round.id == round_id)
                .values(revealed_count=Round.revealed_count + score)
                .returning(Round.revealed_count)
            )
            result = await session.execute(update_stmt)
            await session.commit()

            return result.scalar_one()

    async def get_score(self, round_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Round.revealed_count).where(Round.id == round_id)
                )
            ).scalar_one_or_none()
