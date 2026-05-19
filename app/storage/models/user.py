from typing import Optional
from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    """Модель пользователя 
    Telegram."""

    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(
        BigInteger, 
        comment="Telegram ID",
        unique=True,
        index=True, 
    )

    first_name: Mapped[str] = mapped_column(
        String(255), 
        comment="Имя"
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(255), 
        default=None, 
        comment="Фамилия"
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(255), 
        default=None, 
        comment="Username",
        index=True,
    )

    lang: Mapped[Optional[str]] = mapped_column(
        String(10), 
        default=None, 
        comment="Код языка"
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        server_default="false",
        comment="Администратор",
        index=True
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False, 
        server_default="false",
        comment="Заблокирован",
        index=True
    )

    def __repr__(self) -> str:
        return (
            f"<User(tg_id={self.tg_id}, "
            f"username={self.username})>"
        )

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
