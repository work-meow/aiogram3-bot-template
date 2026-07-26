"""drop dead indexes and use timestamptz

Revision ID: de9a528c7d57
Revises: 0c5669e7dd95
Create Date: 2026-07-26 16:11:26.475965
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Идентификаторы ревизий Alembic
revision: str = "de9a528c7d57"
down_revision: str | Sequence[str] | None = "0c5669e7dd95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Мёртвые и дублирующие индексы: (индекс, таблица, колонка).
# ix_users_tg_id НЕ трогаем — на нём держится
# ON CONFLICT (tg_id) в User._create.
DEAD_INDEXES = (
    # ни одного WHERE по этим колонкам
    ("ix_users_username", "users", "username"),
    ("ix_users_is_admin", "users", "is_admin"),
    ("ix_users_is_banned", "users", "is_banned"),
    ("ix_metrics_name", "metrics", "name"),
    ("ix_fsm_states_chat_id", "fsm_states", "chat_id"),
    ("ix_fsm_states_user_id", "fsm_states", "user_id"),
    # дублирует префикс uq_metric_identity
    ("ix_metrics_service", "metrics", "service"),
    # дублирует префикс uq_fsm_composite_key
    ("ix_fsm_states_bot_id", "fsm_states", "bot_id"),
)

STAMPED = (
    ("users", "created_at"),
    ("users", "updated_at"),
    ("fsm_states", "created_at"),
    ("fsm_states", "updated_at"),
    ("metrics", "created_at"),
    ("metrics", "updated_at"),
)


def upgrade() -> None:
    """Применение миграции."""

    # 1. Снимаем лишнюю запись в B-tree
    for name, table, _ in DEAD_INDEXES:
        op.drop_index(op.f(name), table_name=table)

    # 2. naive -> timestamptz. Значения писал
    # server_default now(), поэтому трактуем их
    # как UTC (контейнеры и планировщик в UTC).
    for table, column in STAMPED:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            existing_server_default=sa.text("now()"),
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )


def downgrade() -> None:
    """Откат миграции."""

    for table, column in STAMPED:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(),
            existing_nullable=False,
            existing_server_default=sa.text("now()"),
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )

    for name, table, column in reversed(DEAD_INDEXES):
        op.create_index(op.f(name), table, [column], unique=False)
