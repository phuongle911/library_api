from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.DAO.job_dao import JobDAO
from app.core.database import get_db, get_read_db

job_router = APIRouter()


@job_router.post("/documents/generate")
async def generate_document(payload: dict, db: AsyncSession = Depends(get_db)):
    job = await JobDAO.create(
        db=db,
        payload=payload,
        type="generate_document"
    )

    return {
        "job_id": job.id,
        "status": job.status
    }


@job_router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_read_db)):
    job = await JobDAO.get_by_id(db, job_id)
    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": str(job.id),
        "status": job.status,
        "result": job.result,
        "error": job.error,
    }
