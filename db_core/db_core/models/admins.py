from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class AdminModel(BaseModel):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
