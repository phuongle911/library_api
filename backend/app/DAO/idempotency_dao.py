from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency_key import IdempotencyKey


class IdempotencyDAO:
    @staticmethod
    async def get(db: AsyncSession, key: str):
        result = await db.execute(
            select(IdempotencyKey).where(IdempotencyKey.key == key)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_processing(db: AsyncSession, key: str):
        record = IdempotencyKey(
            key=key,
            status="processing",
        )
        db.add(record)
        await db.flush()
        return record
    
    @staticmethod
    async def mark_completed(db: AsyncSession, record: IdempotencyKey, response: dict):
        record.status = "completed"
        record.response = response
        await db.flush()
        return record
