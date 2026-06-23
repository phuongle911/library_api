"""add borrow sagas table

Revision ID: 57dbd940aba7
Revises: aa903b5e1185
Create Date: 2026-06-19 12:43:27.376663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57dbd940aba7'
down_revision: Union[str, Sequence[str], None] = 'aa903b5e1185'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "borrow_sagas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_borrow_sagas_id"),
        "borrow_sagas",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_borrow_sagas_user_id"),
        "borrow_sagas",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_borrow_sagas_book_id"),
        "borrow_sagas",
        ["book_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_borrow_sagas_book_id"),
        table_name="borrow_sagas",
    )

    op.drop_index(
        op.f("ix_borrow_sagas_user_id"),
        table_name="borrow_sagas",
    )

    op.drop_index(
        op.f("ix_borrow_sagas_id"),
        table_name="borrow_sagas",
    )

    op.drop_table("borrow_sagas")
