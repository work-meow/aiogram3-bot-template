from typing import Optional
from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BigInteger, String, Boolean, select, func
from sqlalchemy.dialects.postgresql import insert
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
        comment="Username"
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
        comment="Администратор"
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False, 
        server_default="false",
        comment="Заблокирован"
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
    async def get_or_create(
        cls,
        session: AsyncSession,
        tg_user: TgUser,
    ) -> tuple["User", bool]:
        """Отдаёт юзера, создавая 
        при первом визите.."""

        if user := await cls.get_by_tg_id(session, tg_user.id):
            user.sync_profile(tg_user)
            return user, False
        
        return await cls._create(session, tg_user), True



    def sync_profile(
        self, 
        tg_user: TgUser
    ) -> None:
        """Подтягивает имя и 
        username из Telegram."""

        fresh = (
            tg_user.first_name or "",
            tg_user.last_name,
            tg_user.username,
        )

        if (
            self.first_name, 
            self.last_name, 
            self.username
        ) != fresh:
            
            (self.first_name,
             self.last_name,
             self.username) = fresh



    @classmethod
    async def _create(
        cls,
        session: AsyncSession,
        tg_user: TgUser,
    ) -> "User":
        """Атомарное создание 
        нового пользователя."""

        stmt = insert(cls).values(
            tg_id=tg_user.id,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name,
            lang=tg_user.language_code,
            username=tg_user.username,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["tg_id"],
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "username": stmt.excluded.username,
                "updated_at": func.now(),
            }
        ).returning(cls)
        return (await session.scalars(stmt)).one()
    
    
    
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