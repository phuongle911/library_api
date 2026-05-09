"""add idempotency keys

Revision ID: a1d1f279c0fa
Revises: ed35f8755ed9
Create Date: 2026-05-03 15:29:35.931278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1d1f279c0fa'
down_revision: Union[str, Sequence[str], None] = 'ed35f8755ed9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "idempotency_keys",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("response", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )


def downgrade():
    op.drop_table("idempotency_keys")
