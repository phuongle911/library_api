import pytest
import uuid

@pytest.mark.asyncio
async def test_signup_success(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    response = await client.post("/api/v1/auth/signup",
                                 json={
                                     "name":"Test User",
                                     "email":unique_email,
                                     "password":"password123",
                                 },
                                 )
    assert response.status_code in (200, 201)

    data = response.json()
    assert "id" in data
    assert data["email"] == unique_email


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    payload = {
        "name":"Test User",
        "email":unique_email,
        "password":"password123",
    }
    response_1 = await client.post("/api/v1/auth/signup", json=payload)
    assert response_1.status_code in (200, 201)
    
    response_2 = await client.post("/api/v1/auth/signup", json=payload)
    assert response_2.status_code == 400

@pytest.mark.asyncio
async def test_signup_missing_name(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    payload = {
        "name":"",
        "email":unique_email,
        "password":"password123",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_signup_missing_password(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    payload = {
        "name":"test user",
        "email":unique_email,
        "password":"",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_signup_missing_email(client):
    payload = {
        "name":"test user",
        "email":"",
        "password":"password123",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422