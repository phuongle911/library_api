import pytest
from datetime import datetime, timedelta

from app.models.job import Job
from app.worker.job_worker import process_job, calculate_backoff_seconds


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


def test_calculate_backoff_seconds():
    assert calculate_backoff_seconds(1) == 2
    assert calculate_backoff_seconds(2) == 4
    assert calculate_backoff_seconds(3) == 8


@pytest.mark.asyncio
async def test_process_job_marks_success(async_session):
    job = Job(
        type="generate_document",
        status="pending",
        payload={"document_name": "file-1"},
        retry_count=0,
        max_retires=3,
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
async def test_process_job_retries_on_transient_error(async_session):
    job = Job(
        type="generate_document",
        status="pending",
        payload={"should_fail_temporaryly": True},
        retry_count=0,
        max_retries=3,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)

    before = datetime.utcnow()

    await process_job(job, async_session)
    await async_session.refresh(job)

    assert job.status == "pending"
    assert job.retry_count == 1
    assert job.error == "Temporary external service failure"
    assert job.next_run_at >= before + timedelta(seconds=2)


@pytest.mark.asyncio
async def test_process_job_marks_failed_when_retries_exhausted(async_session):
    job = Job(
        type="generate_document",
        status="pending",
        payload={"should_fail_temporarily": True},
        retry_count=3,
        max_retries=3,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)

    await process_job(job, async_session)
    await async_session.refresh(job)

    assert job.status == "failed"
    assert job.retry_count == 4
    assert job.error == "Temporary external service failure"
