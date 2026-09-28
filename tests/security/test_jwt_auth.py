"""Security tests for JWT validation, signature verification, and account deactivation."""
import httpx
import pytest

from app.core.auth import create_access_token
from app.models.user import User
from tests.utils import create_expired_jwt, create_test_jwt


@pytest.mark.security
async def test_jwt_missing_header(client: httpx.AsyncClient):
    """Test accessing protected route without Authorization header yields 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.security
async def test_jwt_malformed_token(client: httpx.AsyncClient):
    """Test accessing protected route with garbage token string yields 401."""
    headers = {"Authorization": "Bearer this_is_not_a_valid_jwt"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.security
async def test_jwt_expired_token(client: httpx.AsyncClient):
    """Test accessing protected route with expired token yields 401."""
    expired_token = create_expired_jwt()
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.security
async def test_jwt_inactive_user_forbidden(
    client: httpx.AsyncClient,
    inactive_user: User,
):
    """Test deactivated user account yields 403 Forbidden when calling get_current_active_user."""
    token = create_access_token(data={"sub": str(inactive_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 403
    data = response.json()
    msg = data.get("detail") or data.get("message") or ""
    assert "deactivated" in str(msg).lower()
