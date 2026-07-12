from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


async def commit_or_rollback(db: AsyncSession):
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise
