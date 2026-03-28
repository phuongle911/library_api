import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import AsyncSessionLocal
from app.DAO.job_dao import JobDAO


def calculate_backoff_seconds(retry_count: int) -> int:
    return 2 ** retry_count

class TransientJobError(Exception):
    pass


async def process_job(job, db: AsyncSession):
    try:
        job.status = "processing"
        await db.commit()

        if job.payload and job.payload.get("should_fail_temporarily"):
            raise TransientJobError("Temporary external service failure")
        
        job.status = "success"
        job.result = {"message": "Job completed successfullly"}
        job.error = None
        await db.commit()

    except TransientJobError as e:
        job.retry_count += 1
        job.error = str(e)

        if job.retry_count >= job.max_retries:
            job.status = "failed"
        else:
            job.status = "pending"
            job.next_run_at = datetime.utcnow() + calculate_backoff_seconds(job.retry_count)
        await db.commit()

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
    
        await db.commit()


async def worker_loop():
    while True:
        async with AsyncSessionLocal() as db:
            job = await JobDAO.get_next_runnable_job(db)

            if job:
                await process_job(job, db)

        await asyncio.sleep(2)  # polling interval


if __name__ == "__main__":
    asyncio.run(worker_loop())