from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Integer,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.store.database.sqlachemy_base import BaseModel


class Question(BaseModel):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    answers = relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question id={self.id} text={self.text[:30]}...>"


class AnswerOption(BaseModel):
    """
    A single answer entry for a question with an associated points/weight.
    For '100 к 1' answers usually have integer points (e.g. 30, 20, 5 ...).
    """
    __tablename__ = "answer_options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<AnswerOption id={self.id} q={self.question_id} text={self.text[:20]} pts={self.points}>"

