import random

from shared_models.questions import Question
from app.store.base.accessor import BaseAccessor
from sqlalchemy import select


class QuestionAccessor(BaseAccessor):
    async def get_question_by_id(self, question_id: int) -> Question | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Question).where(Question.id == question_id)
            )
            return result.scalar_one_or_none()

    async def check_answer(self, question_id: int, answer: str) -> bool:
        question = await self.get_question_by_id(question_id)
        if not question:
            return False
        return question.answer.strip().lower() == answer.strip().lower()

    async def get_random_question(self) -> Question | None:
        async with self.app.database.session() as session:
            result = await session.execute(select(Question))
            questions = result.scalars().all()
            if not questions:
                return None

            return random.choice(questions)
