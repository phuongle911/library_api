import pytest

from app.models.job import Job
from app.worker.job_worker import process_job


@pytest.mark.asyncio
async def test_process_job_marks_job_success(async_session):
    job = Job(
        type="generate_document",
        status="pending",
        payload={"document_name": "file-1"},
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)

    await process_job(job, async_session)
    await async_session.refresh(job)

    assert job.status == "success"
    assert job.result == {"message": "Document generated successfully"}
    assert job.error is None


@pytest.mark.asyncio
async def test_process_job_marks_job_failed_when_exception(
    async_session,
    monkeypatch,
):
    job = Job(
        type="generate_document",
        status="pending",
        payload={"document_name": "file-2"},
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)


    async def failing_sleep(*args, **kwargs):
        raise Exception("Simulated worker failure")

    monkeypatch.setattr("app.worker.job_worker.asyncio.sleep", failing_sleep)

    await process_job(job, async_session)
    await async_session.refresh(job)

    assert job.status == "failed"
    assert job.error == "Simulated worker failure"
    assert job.result is None

