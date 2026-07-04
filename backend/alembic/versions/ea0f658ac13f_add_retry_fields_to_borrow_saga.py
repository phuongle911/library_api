"""add retry fields to borrow saga

Revision ID: ea0f658ac13f
Revises: 36bf6ba6c393
Create Date: 2026-07-04 08:15:44.315779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ea0f658ac13f'
down_revision: Union[str, Sequence[str], None] = '36bf6ba6c393'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "borrow_sagas",
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "borrow_sagas",
        sa.Column(
            "last_error",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "borrow_sagas",
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.alter_column(
        "borrow_sagas",
        "retry_count",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("borrow_sagas", "completed_at")
    op.drop_column("borrow_sagas", "last_error")
    op.drop_column("borrow_sagas", "retry_count")
