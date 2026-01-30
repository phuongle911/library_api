from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
async def create_refresh_token_row(
    db: AsyncSession,
    user_id: int,
    token_hash: str,
    expires_at,
) -> RefreshToken:
    row = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
async def get_refresh_token_row(db: AsyncSession, token_hash: str) -> RefreshToken | None:
    res = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return res.scalar_one_or_none()
def is_refresh_token_valid(row: RefreshToken) -> bool:
    now = datetime.now(timezone.utc)
    if row.revoked_at is not None:
        return False
    if row.expires_at <= now:
        return False
    return True
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
async def create_refresh_token_row(
    db: AsyncSession,
    user_id: int,
    token_hash: str,
    expires_at,
) -> RefreshToken:
    row = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
async def get_refresh_token_row(db: AsyncSession, token_hash: str) -> RefreshToken | None:
    res = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return res.scalar_one_or_none()
def is_refresh_token_valid(row: RefreshToken) -> bool:
    now = datetime.now(timezone.utc)
    if row.revoked_at is not None:
        return False
    if row.expires_at <= now:
        return False
    return True
