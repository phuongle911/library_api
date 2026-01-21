import pytest
from httpx import AsyncClient
from httpx import ASGITransport
import uuid

from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        ) as ac: 
        yield ac

@pytest.fixture
async def auth_headers(client):
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    
    await client.post("/api/v1/auth/signup", json={
        "name":"Tesst User",
        "email":email,
        "password":password,
    },
    )

    login_response = await client.post("/api/v1/auth/login", json={
        "email":email,
        "password":password,
    },
    )
    
    data = login_response.json()
    token = data["access_token"]

    return {
        "Authorization": f"Bearer{token}"
    }