from typing import Any, Self
from sqlalchemy.sql import func
from collections.abc import Sequence
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, UniqueConstraint, text, select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseModel


class Metric(BaseModel):
    """Универсальная таблица 
    для персистентного хранения 
    метрик всей системы."""


    __tablename__ = "metrics"

    service: Mapped[str] = mapped_column(
        String(50), 
        index=True,
        comment="Источник"
    )

    name: Mapped[str] = mapped_column(
        String(255), 
        index=True,
        comment="Название"
    )

    labels: Mapped[dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Метки в формате JSON"
    )

    value: Mapped[float] = mapped_column(
        Float, 
        default=0.0,
        comment="Значение метрики"
    )

    __table_args__ = (
        UniqueConstraint(
            "service", "name", "labels", 
            name="uq_metric_identity"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Metric(service={self.service}, "
            f"name={self.name}, value={self.value})>"
        )



    @classmethod
    async def get_by_service(
        cls, 
        session: AsyncSession, 
        service: str
    ) -> Sequence[Self]:
        """Получить метрики 
        конкретного сервиса."""
        
        stmt = select(cls).where(cls.service == service)
        result = await session.scalars(stmt)
        return result.all()



    @classmethod
    async def bulk_upsert(
        cls,
        session: AsyncSession,
        records: list[dict[str, Any]]
    ) -> None:
        """Сохраняет/обновляет метрики 
        со всей системы."""
        
        if not records:
            return
        
        stmt = insert(cls).values(records)
        await session.execute(
            stmt.on_conflict_do_update(
                index_elements=[
                    'service', 
                    'labels',
                    'name'
                ],
                set_={
                    'value': stmt.excluded.value,
                    'updated_at': func.now()
                }
            )
        )