from typing import TYPE_CHECKING

from app.questions.models import AnswerOption, Question
from app.store.base.accessor import BaseAccessor
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.web.app import Application


class QuestionsAccessor(BaseAccessor):
    def __init__(self, app: "Application"):
        self.app = app

    async def create_question(self, data):
        async with self.app.database.session() as session:
            question = Question(text=data["text"])
            session.add(question)
            await session.flush()

            for answer_data in data["answers"]:
                answer = AnswerOption(question=question, **answer_data)
                session.add(answer)

            await session.flush()
            await session.refresh(question, ["answers"])

            await session.commit()
            return question

    async def get_questions(self, limit: int = 10, offset: int = 0):
        """Получить список вопросов с answers (с пагинацией)."""
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Question)
                .options(selectinload(Question.answers))
                .order_by(Question.id)
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()

    async def count_questions(self) -> int:
        """Посчитать общее количество вопросов (для страниц)."""
        async with self.app.database.session() as session:
            result = await session.execute(select(func.count(Question.id)))
            return result.scalar_one()

    async def delete_question(self, data: dict) -> Question:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Question).where(Question.id == data["id"])
            )
            question = result.scalar_one_or_none()

            if question:
                await session.delete(question)
                await session.commit()
                return question
            return None
