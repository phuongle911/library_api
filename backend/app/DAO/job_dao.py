from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from datetime import datetime

from app.models.job import Job


class JobDAO:

    @staticmethod
    async def create(db: AsyncSession, payload: dict, type: str) -> Job:
        job = Job(type=type, payload=payload, next_run_at=datetime.utcnow())
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

    @staticmethod
    async def get_next_runnable_job(db: AsyncSession):
        stm = (
            select(Job)
            .where(
                Job.status == "pending",
                or_(
                Job.next_run_at.is_(None),
                Job.next_run_at <= datetime.utcnow(),
                ),
                )
            .order_by(Job.created_at)
            .with_for_update(skip_locked=True)
            .limit(1)
            )

        result = await db.execute(stm)
        return result.scalar_one_or_none()
