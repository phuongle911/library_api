import os
import uuid

import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base
from app.models.user import User




TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@db:5432/app_test"


@pytest.fixture(scope="session")
def anyio_backend():
    # stabilizes async tests in many environments
    return "asyncio"


@pytest.fixture(scope="session")
async def async_engine():
    # :white_check_mark: create engine inside fixture + NullPool to avoid stale/closed pooled conns
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        poolclass=NullPool,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def prepare_test_database(async_engine):
    """
    Create tables once per test session, drop at the end.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_session(async_engine):
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def owner_user(async_session):
    u = User(
        name="Test Owner",
        email=f"owner_{uuid.uuid4()}@example.com",
        hashed_password="fake-hash",
        is_active=True,
        role="user",
    )
    async_session.add(u)
    await async_session.commit()
    await async_session.refresh(u)
    return u




@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"

    await client.post(
        "/api/v1/auth/signup",
        json={"name": "Test User", "email": email, "password": password},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_owner_user(async_session):
    u = User(
        name="Ann",
        email=f"other_{uuid.uuid4()}@gmail.com",
        hashed_password="fake-hash",
        is_active=True,
        role="user",
    )
    async_session.add(u)
    await async_session.commit()
    await async_session.refresh(u)
    return u
