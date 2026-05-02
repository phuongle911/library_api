"""add active borrow unique index

Revision ID: 6faaa4f7fdb4
Revises: 58cb85b776e9
Create Date: 2026-05-02 14:42:56.907821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6faaa4f7fdb4'
down_revision: Union[str, Sequence[str], None] = '58cb85b776e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index(
        "uq_active_borrow",
        "borrow_records",
        ["user_id", "book_id"],
        unique=True,
        postgresql_where=sa.text("returned_at IS NULL"),
    )


def downgrade():
    op.drop_index(
        "uq_active_borrow",
        table_name="borrow_records",
    )
