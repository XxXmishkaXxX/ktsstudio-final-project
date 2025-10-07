import enum

from app.games.models.questions import AnswerOption, Question  # noqa: F401
from app.store.database.sqlachemy_base import BaseModel
from sqlalchemy import (
    JSON,
    BigInteger,
    Enum,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RoundState(enum.Enum):
    faceoff = "faceoff"
    buzzer_answer = "buzzer_answer"
    team_play = "team_play"
    finished = "finished"


class Round(BaseModel):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )

    round_number: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    state: Mapped[RoundState] = mapped_column(
        Enum(RoundState), default=RoundState.faceoff, nullable=False
    )

    revealed_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    current_buzzer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    current_team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )

    temp_answer: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    game = relationship("Game", back_populates="rounds", foreign_keys=[game_id])
    question = relationship("Question", lazy="joined")
    round_answers: Mapped[list["RoundAnswer"]] = relationship(
        "RoundAnswer",
        back_populates="round",
        cascade="all, delete-orphan",
    )
    current_buzzer = relationship("User", foreign_keys=[current_buzzer_id])
    current_team = relationship("Team", foreign_keys=[current_team_id])

    def __repr__(self):
        return (
            f"<Round id={self.id} game_id={self.game_id}"
            f" q={self.question_id} #={self.round_number}"
            f" state={self.state.value} buzzer={self.current_buzzer_id}"
            f" team={self.current_team_id}>"
        )


class RoundAnswer(BaseModel):
    __tablename__ = "round_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_option_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("answer_options.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round: Mapped["Round"] = relationship(
        "Round", back_populates="round_answers"
    )
    answer_option: Mapped["AnswerOption"] = relationship(
        "AnswerOption", lazy="selectin"
    )
