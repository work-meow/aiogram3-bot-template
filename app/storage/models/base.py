import uuid6

from datetime import datetime
from sqlalchemy import func, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referenced_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BaseModel(DeclarativeBase):
    """Базовый класс с UUID7 и системными полями."""

    id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid6.uuid7,
        sort_order=-1,
        comment="Идентификатор записи"
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        sort_order=999,
        comment="Дата создания записи"
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        sort_order=1000,
        comment="Дата последнего обновления"
    )

    metadata = MetaData(naming_convention=CONVENTION)

    def __repr__(self) -> str:
        """Для удобной отладки в логах."""
        return f"<{self.__class__.__name__}(id={self.id})>"