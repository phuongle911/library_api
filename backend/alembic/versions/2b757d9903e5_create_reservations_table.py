"""create reservations table

Revision ID: 2b757d9903e5
Revises: ea0f658ac13f
Create Date: 2026-07-07 10:11:35.906252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2b757d9903e5'
down_revision: Union[str, Sequence[str], None] = 'ea0f658ac13f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_book_id"), "reservations", ["book_id"], unique=False)
    op.create_index(op.f("ix_reservations_id"), "reservations", ["id"], unique=False)
    op.create_index(op.f("ix_reservations_user_id"), "reservations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reservations_user_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_book_id"), table_name="reservations")
    op.drop_table("reservations")
