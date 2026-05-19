from typing import Optional
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BigInteger, String, Boolean, select
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
        default="ru", 
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



    @classmethod
    async def create_new(
        cls,
        session: AsyncSession,
        tg_user: TgUser,
    ) -> "User":
        """Создаёт нового 
        пользователя."""
        
        user = cls(
            tg_id=tg_user.id,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name,
            lang=tg_user.language_code,
            username=tg_user.username,
        )
        
        session.add(user)
        await session.commit()
        return user
    
    
    
    @classmethod
    async def get_by_tg_id(
        cls,
        session: AsyncSession,
        tg_id: int,
    ) -> "User | None":
        """Находит пользователя 
        по Telegram ID."""
        
        return await session.scalar(
            select(cls).where(
                cls.tg_id == 
                tg_id
            )
        )