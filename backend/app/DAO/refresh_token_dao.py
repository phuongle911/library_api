from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from datetime import datetime, timezone
from app.core.transactions import commit_or_rollback


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
    await commit_or_rollback(db)
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
    await commit_or_rollback(db)
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


async def get_refresh_token_by_hash(db: AsyncSession, token_hash:str):
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_tokens_for_user(
        db: AsyncSession,
        user_id: int
):
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await commit_or_rollback(db)


async def revoke_refresh_token(db, token_hash: str):
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None)
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await commit_or_rollback(db)