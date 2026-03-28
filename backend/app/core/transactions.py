from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.db_errors import map_db_error


async def commit_or_rollback(db: AsyncSession):
    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        print("REAL DB ERROR:", repr(exc))
        raise
    