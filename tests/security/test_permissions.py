"""Security tests for Role-Based Access Control and fine-grained permissions."""
import httpx
import pytest

from app.models.user import User


@pytest.mark.security
async def test_admin_route_forbidden_for_standard_user(
    authenticated_client: httpx.AsyncClient,
    test_user: User,
):
    """Test standard (non-admin) user is rejected with 403 on admin routes."""
    response = await authenticated_client.get("/admin/cache")
    assert response.status_code == 403
    assert "administrative" in response.json()["detail"].lower()


@pytest.mark.security
async def test_admin_route_allowed_for_admin_user(
    admin_client: httpx.AsyncClient,
    admin_user: User,
):
    """Test admin user is permitted on admin routes."""
    response = await admin_client.get("/admin/cache")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data or "connected" in data or "ping_ms" in data
