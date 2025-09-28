import enum
from datetime import datetime

from app.store.database.sqlachemy_base import BaseModel
from sqlalchemy import BigInteger, DateTime, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class State(enum.Enum):
    idle = "idle" 
    in_game = "in_game"
    write_answer = "write_answer"



class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    state: Mapped["UserState"] = relationship(
        "UserState", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg_id={self.tg_id} username={self.username}>"


class UserState(BaseModel):
    __tablename__ = "users_states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[State] = mapped_column(Enum(State), default=State.idle, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="state")

    def __repr__(self) -> str:
        return f"<UserState user_id={self.user_id} state={self.state}>"
