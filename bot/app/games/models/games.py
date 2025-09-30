import enum
from datetime import datetime

from app.games.models.questions import Question  # noqa: F401
from app.store.database.sqlachemy_base import BaseModel
from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GameState(enum.Enum):
    created = "created"
    starting = "starting"
    in_progress = "in_progress"
    finished = "finished"


class RoundState(enum.Enum):
    waiting = "waiting"
    open = "open"
    finished = "finished"


class Game(BaseModel):
    __tablename__ = "games"
    __table_args__ = (Index("ix_games_chat_state", "chat_id", "state"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    state: Mapped[GameState] = mapped_column(
        Enum(GameState), default=GameState.created, nullable=False
    )

    current_round_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "rounds.id", use_alter=True, name="fk_games_current_round_id"
        ),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    teams = relationship(
        "Team", back_populates="game", cascade="all, delete-orphan"
    )
    rounds = relationship(
        "Round",
        back_populates="game",
        cascade="all, delete-orphan",
        foreign_keys="[Round.game_id]",
    )

    def __repr__(self):
        return (
            f"<Game id={self.id} chat_id={self.chat_id}"
            f"status={self.state.value}>"
        )


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
        Enum(RoundState), default=RoundState.waiting, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    timer_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revealed_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    game = relationship("Game", back_populates="rounds", foreign_keys=[game_id])
    question = relationship("Question")

    def __repr__(self):
        return (
            f"<Round id={self.id} game_id={self.game_id}"
            f"q={self.question_id} #={self.round_number}"
            f"status={self.state.value}>"
        )
