from datetime import datetime

from app.store.database.sqlachemy_base import BaseModel
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Question(BaseModel):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    answers = relationship(
        "AnswerOption",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Question id={self.id} text={self.text[:30]}...>"


class AnswerOption(BaseModel):
    __tablename__ = "answer_options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return (
            f"<AnswerOption id={self.id} q={self.question_id} "
            f"text={self.text[:20]} pts={self.points}>"
        )
