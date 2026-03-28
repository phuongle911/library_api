from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.job import Job


class JobDAO:

    @staticmethod
    async def create(db: AsyncSession, payload: dict, type: str) -> Job:
        job = Job(type=type, payload=payload)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job
    
    @staticmethod
    async def get_by_id(db: AsyncSession, job_id: int) -> Job | None:
        result = await db.execute(select(Job).where(Job.id == job_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_pending_job(db: AsyncSession) -> Job | None:
        result = await db.execute(
            select(Job)
            .where(Job.status == "pending")
            .limit(1)
        )
        return result.scalars().first()