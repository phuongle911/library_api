"""change users.role from enum to varchar

Revision ID: e48316c85bd3
Revises: 6a287e1dab39
Create Date: 2026-02-14 15:45:45.937524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e48316c85bd3'
down_revision: Union[str, Sequence[str], None] = '6a287e1dab39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Drop default (important when changing type)
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")

    # 2) Convert enum -> varchar
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::text")

    # 3) Restore default
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'user'")

    # 4) Drop enum type if it exists (and not used elesewhere)
    op.execute("DROP TYPE IF EXISTS user_role")


def downgrade() -> None:
    # Recreate enum type
    op.execute("CREATE TYPE user_role AS ENUM ('user, 'admin')")

    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")

    # Convert varchar -> enum (cast)
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role:user_role")

    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'user'")
