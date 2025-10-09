import enum
from datetime import datetime

from .base import BaseModel
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
            f" status={self.state.value}>"
        )
