"""add borrow history read model

Revision ID: 36bf6ba6c393
Revises: 57dbd940aba7
Create Date: 2026-06-23 13:42:19.465718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '36bf6ba6c393'
down_revision: Union[str, Sequence[str], None] = '57dbd940aba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'borrow_history_read_models',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('borrow_record_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('book_title', sa.String(), nullable=False),
        sa.Column('borrow_status', sa.String(), nullable=False),
        sa.Column('borrowed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('returned_at', sa.DateTime(timezone=True), nullable=True),

        # NOTE: fix create_at -> created_at
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),

        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),

        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_borrow_history_read_models_book_id'),
        'borrow_history_read_models',
        ['book_id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_borrow_history_read_models_borrow_record_id'),
        'borrow_history_read_models',
        ['borrow_record_id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_borrow_history_read_models_id'),
        'borrow_history_read_models',
        ['id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_borrow_history_read_models_user_id'),
        'borrow_history_read_models',
        ['user_id'],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(
        op.f('ix_borrow_history_read_models_user_id'),
        table_name='borrow_history_read_models',
    )

    op.drop_index(
        op.f('ix_borrow_history_read_models_id'),
        table_name='borrow_history_read_models',
    )

    op.drop_index(
        op.f('ix_borrow_history_read_models_borrow_record_id'),
        table_name='borrow_history_read_models',
    )

    op.drop_index(
        op.f('ix_borrow_history_read_models_book_id'),
        table_name='borrow_history_read_models',
    )

    op.drop_table('borrow_history_read_models')
