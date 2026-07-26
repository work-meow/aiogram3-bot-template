"""add fsm updated_at index

Revision ID: 0c5669e7dd95
Revises: 63933d4f952f
Create Date: 2026-07-26 14:43:13.073623
"""

from collections.abc import Sequence

from alembic import op

# Идентификаторы ревизий Alembic
revision: str = "0c5669e7dd95"
down_revision: str | Sequence[str] | None = "63933d4f952f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Применение миграции."""
    # get_active/cleanup фильтруют по updated_at:
    # без индекса это Seq Scan по всей fsm_states
    op.create_index(
        op.f("ix_fsm_states_updated_at"),
        "fsm_states",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Откат миграции."""
    op.drop_index(
        op.f("ix_fsm_states_updated_at"),
        table_name="fsm_states",
    )
