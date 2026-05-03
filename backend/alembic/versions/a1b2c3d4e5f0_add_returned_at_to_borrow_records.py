"""add returned_at to borrow_records

Revision ID: a1b2c3d4e5f0
Revises: 58cb85b776e9
Create Date: 2026-05-03

Required before partial index uq_active_borrow (6faaa4f7fdb4), which uses returned_at.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f0"
down_revision: Union[str, Sequence[str], None] = "58cb85b776e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE borrow_records
        ADD COLUMN IF NOT EXISTS returned_at TIMESTAMP WITH TIME ZONE;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE borrow_records DROP COLUMN IF EXISTS returned_at")
