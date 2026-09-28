"""Security tests for API Key authentication, scope validation, and revocation."""
from datetime import datetime, timedelta, timezone
import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.api_key_service import api_key_service
from tests.factories.additional_factories import APIKeyFactory


@pytest.mark.security
async def test_api_key_auth_success(
    client: httpx.AsyncClient,
    test_user: User,
    db_session: AsyncSession,
):
    """Test accessing protected /auth/me using valid X-API-Key header."""
    raw_key = "cp_live_valid_key_1234567890abcdef"
    await APIKeyFactory.create(
        db=db_session,
        user_id=test_user.id,
        raw_key=raw_key,
        is_active=True,
        permissions=["*"],
    )

    headers = {"X-API-Key": raw_key}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["username"] == test_user.username


@pytest.mark.security
async def test_api_key_revoked_rejection(
    client: httpx.AsyncClient,
    test_user: User,
    db_session: AsyncSession,
):
    """Test that deactivated API Key is rejected with 401 Unauthorized."""
    raw_key = "cp_live_revoked_key_1234567890abcdef"
    await APIKeyFactory.create(
        db=db_session,
        user_id=test_user.id,
        raw_key=raw_key,
        is_active=False,  # Revoked
    )

    headers = {"X-API-Key": raw_key}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.security
async def test_api_key_invalid_rejection(client: httpx.AsyncClient):
    """Test that a nonexistent/invalid API Key is rejected with 401."""
    headers = {"X-API-Key": "cp_live_completely_fake_key_9999"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401
