"""Integration tests for authentication API endpoints."""
import httpx
import pytest

from app.models.user import User


@pytest.mark.integration
async def test_api_register_success(client: httpx.AsyncClient):
    """Test POST /auth/register endpoint."""
    payload = {
        "username": "api_new_user",
        "email": "api_new_user@example.com",
        "password": "Password123!",
        "full_name": "API New User",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "api_new_user"
    assert data["data"]["email"] == "api_new_user@example.com"


@pytest.mark.integration
async def test_api_register_duplicate(client: httpx.AsyncClient, test_user: User):
    """Test POST /auth/register duplicate rejection."""
    payload = {
        "username": test_user.username,
        "email": "another_mail@example.com",
        "password": "Password123!",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.integration
async def test_api_login_success(client: httpx.AsyncClient, test_user: User):
    """Test POST /auth/login with valid JSON credentials."""
    payload = {
        "username_or_email": test_user.username,
        "password": "TestPass123!",
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    token_dict = data.get("data") if isinstance(data, dict) and "data" in data else data
    assert "access_token" in token_dict
    assert "refresh_token" in token_dict
    assert token_dict.get("token_type") == "bearer"



@pytest.mark.integration
async def test_api_login_invalid_password(client: httpx.AsyncClient, test_user: User):
    """Test POST /auth/login failure with wrong password."""
    payload = {
        "username_or_email": test_user.username,
        "password": "WrongPassword123!",
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401


@pytest.mark.integration
async def test_api_me_authenticated(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test GET /auth/me returns current authenticated user profile."""
    response = await authenticated_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["username"] == test_user.username
    assert data["data"]["email"] == test_user.email


@pytest.mark.integration
async def test_api_me_unauthenticated(client: httpx.AsyncClient):
    """Test GET /auth/me fails when Authorization header is absent."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.integration
async def test_api_refresh_token(client: httpx.AsyncClient, test_user: User):
    """Test POST /auth/refresh with valid refresh token."""
    from app.core.auth import create_refresh_token

    ref_token = create_refresh_token(data={"sub": str(test_user.id)})
    response = await client.post("/auth/refresh", json={"refresh_token": ref_token})
    assert response.status_code == 200
    data = response.json()
    token_dict = data.get("data") if isinstance(data, dict) and "data" in data else data
    assert "access_token" in token_dict

