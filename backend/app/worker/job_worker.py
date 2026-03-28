import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.DAO.job_dao import JobDAO


async def process_job(job, db: AsyncSession):
    try:
        job.status = "processing"
        await db.commit()

        # simulate long task
        await asyncio.sleep(5)

        job.status = "success"
        job.result = {"message": "Document generated successfully"}

        await db.commit()

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        await db.commit()


async def worker_loop():
    while True:
        async with asyn_session_maker() as db:
            job = await JobDAO.get_pending_job(db)

            if job:
                await process_job(job, db)

        await asyncio.sleep(2)  # polling interval


if __name__ == "__main__":
    asyncio.run(worker_loop())