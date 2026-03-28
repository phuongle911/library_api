import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.job import Job


@pytest.mark.asyncio
async def test_generate_document_creates_pending_job(
    client: AsyncClient,
    async_session,
):
    payload = {
        "document_name": "test-doc",
        "template": "basic",
    }

    response = await client.post("/api/v1/documents/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "job_id) in data"
    assert data["status"] == "pending"

    result = await async_session.execute(select(Job).where(Job.id == data["job_id"]))
    job = result.scalars().first()

    assert job is not None
    assert job.type == "generate_document"
    assert job.status == "pending"
    assert job.payload == payload
    assert job.result is None
    assert job.error is None


@pytest.mark.asyncio
async def test_get_job_status_return_job_details(
    client: AsyncClient,
    async_session,
):
    job = Job(
        type="generate_document",
        status="success",
        payload={"document_name": "abc"},
        result={"message": "Document generate successfully"},
        error=None,
    )
    async_session.add(job)
    await async_session.commit()
    await async_session.refresh(job)

    response = await client.get(f"/api/v1/jobs/{job.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["job_id"] == job.id
    assert data["status"] == "success"
    assert data["result"] == {"message": "Document generate successfully"}


@pytest.mark.asyncio
async def test_get_job_status_return_not_found_for_invalid_job(
    client: AsyncClient,
):
    response = await client.get("/jobs/999999")

    assert response.status_code == 404
    data = response.json()
    print(f"error spot {data}")

    assert "error" in data
    error = data["error"]
    assert error["code"] == "HTTP_ERROR"
    assert error["message"] == "Not Found"
    assert "request_id" in error
