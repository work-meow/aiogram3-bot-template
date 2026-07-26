from typing import Sequence, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BigInteger, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy import select, delete, tuple_, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import BaseModel


TTL = text("INTERVAL '30 days'")


class StorageState(BaseModel):
    """Слепки FSM состояний 
    с трекингом активности."""

    __tablename__ = "fsm_states"

    bot_id: Mapped[int] = mapped_column(
        BigInteger, 
        comment="ID бота"
    )
    
    chat_id: Mapped[int] = mapped_column(
        BigInteger, 
        comment="ID чата"
    )
    
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        comment="ID юзера"
    )
    
    destiny: Mapped[str] = mapped_column(
        String, 
        comment="Маркер изоляции"
    )
    
    state: Mapped[str | None] = mapped_column(
        String, 
        nullable=True, 
        comment="Текущий стейт"
    )
    
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        comment="Данные FSM"
    )

    __table_args__ = (
        UniqueConstraint(
            "bot_id", "chat_id",
            "user_id", "destiny",
            name="uq_fsm_composite_key"
        ),
        Index(
            "ix_fsm_states_updated_at",
            "updated_at"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<FSM(user_id={self.user_id}, "
            f"state={self.state})>"
        )



    @classmethod
    async def get_active(
        cls,
        session: AsyncSession,
        limit: int = 200_000
    ) -> Sequence[Any]:
        """Получает только свежие
        состояния за 30 дней."""

        stmt = (
            select(
                cls.bot_id,
                cls.chat_id,
                cls.user_id,
                cls.destiny,
                cls.state,
                cls.data
            )
            .where(
                cls.updated_at >= 
                func.now() - TTL
            )
            .limit(limit)
        )
        return (await session.execute(stmt)).all()



    @classmethod
    async def bulk_delete(
        cls,
        session: AsyncSession,
        keys: list[tuple[int, int, int, str]]
    ) -> None:
        """Пакетно сносит 
        завершенные цепочки."""
        
        if not keys:
            return

        await session.execute(
            delete(cls).where(
                tuple_(
                    cls.bot_id,
                    cls.chat_id,
                    cls.user_id,
                    cls.destiny
                ).in_(keys)
            ),
            execution_options={
                "synchronize_session": False
            }
        )



    @classmethod
    async def bulk_upsert(
        cls,
        session: AsyncSession,
        records: list[dict[str, Any]]
    ) -> None:
        """Пакетно обновляет 
        активные стейты (UPSERT)."""
        
        if not records:
            return

        stmt = insert(cls).values(records)
        await session.execute(
            stmt.on_conflict_do_update(
                index_elements=[
                    'bot_id', 
                    'chat_id', 
                    'user_id',
                    'destiny'
                ],
                set_={
                    'state': stmt.excluded.state,
                    'data': stmt.excluded.data,
                    'updated_at': func.now()
                }
            )
        )



    @classmethod
    async def cleanup(
        cls,
        session: AsyncSession
    ) -> None:
        """Очищает базу от 
        заброшенных сессий."""
        
        await session.execute(
            delete(cls).where(
                cls.updated_at <
                func.now()
                - TTL
            ),
            execution_options={
                "synchronize_session": False
            }
        )