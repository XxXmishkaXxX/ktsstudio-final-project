import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Integer,
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship



from app.store.database.sqlachemy_base import BaseModel


class GameStatus(enum.Enum):
    created = "created"
    in_progress = "in_progress"
    paused = "paused"
    finished = "finished"

class RoundStatus(enum.Enum):
    waiting = "waiting"
    open = "open"     
    finished = "finished"


class Game(BaseModel):
    __tablename__ = "games"
    __table_args__ = (
        Index("ix_games_chat_status", "chat_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), default=GameStatus.created, nullable=False)

    current_round_id: Mapped[int | None] = mapped_column(
                        Integer,
                        ForeignKey("rounds.id", use_alter=True, name="fk_games_current_round_id"),
                        nullable=True
                    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    teams = relationship("Team", back_populates="game", cascade="all, delete-orphan")
    rounds = relationship("Round", back_populates="game", cascade="all, delete-orphan")
    events = relationship("GameEvent", back_populates="game")

    def __repr__(self):
        return f"<Game id={self.id} chat_id={self.chat_id} status={self.status.value}>"


class Round(BaseModel):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[RoundStatus] = mapped_column(Enum(RoundStatus), default=RoundStatus.waiting, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    timer_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    revealed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    game = relationship("Game", back_populates="rounds")
    question = relationship("Question")

    def __repr__(self):
        return f"<Round id={self.id} game_id={self.game_id} q={self.question_id} #={self.round_number} status={self.status.value}>"
