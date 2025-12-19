import pytest
import uuid

@pytest.mark.asyncio
async def test_login_success(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    response_signup = await client.post("/api/v1/auth/signup",
                                 json={
                                     "name":"Test User",
                                     "email":unique_email,
                                     "password":"password123",
                                 },
                                 )
    assert response_signup.status_code in (200, 201)
    response_login = await client.post(
        "api/v1/auth/login",
        json={
            "email":unique_email,
            "password":"password123"
        },
    )
    assert response_login.status_code == 200

    data = response_login.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    response_signup = await client.post("/api/v1/auth/signup",
                                 json={
                                     "name":"Test User",
                                     "email":unique_email,
                                     "password":"password123",
                                 },
                                 )
    assert response_signup.status_code in (200, 201)
    response_login = await client.post(
        "api/v1/auth/login",
        json={
            "email":unique_email,
            "password":"password_wrong"
        },
    )
    assert response_login.status_code == 401

@pytest.mark.asyncio
async def test_login_unkonwn_user(client):
    response = await client.post(
        "api/v1/auth/login",
        json={
            "email":"anything@example.com",
            "password":"password123"
        },
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_missing_password(client):
    unique_email = f"user_{uuid.uuid4()}@example.com"
    response_login = await client.post(
        "api/v1/auth/login",
        json={
            "email":unique_email,
            "password":""
        },
    )
    assert response_login.status_code == 422

