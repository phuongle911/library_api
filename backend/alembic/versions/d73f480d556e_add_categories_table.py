"""add categories table

Revision ID: d73f480d556e
Revises: e48316c85bd3
Create Date: 2026-03-07 16:04:31.128260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd73f480d556e'
down_revision: Union[str, Sequence[str], None] = 'e48316c85bd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
       "categories",
       sa.Column("id", sa.Integer(), nullable=False),
       sa.Column("name",sa.String(length=100), nullable=False),
       sa.Column("description", sa.Text(), nullable=True),
       sa.PrimaryKeyConstraint("id", name=op.f("categories_pkey"))
   )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")