"""Integration tests for Webhook subscription management and testing dispatches."""
import uuid
import httpx
import pytest
from unittest.mock import AsyncMock, patch

from app.models.user import User


@pytest.mark.integration
async def test_api_create_webhook(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /webhooks creates a new webhook subscription."""
    payload = {
        "url": "https://example.com/api/webhook-receiver",
        "secret": "whsec_super_secret_test_token_12345",
        "event_type": "review.completed",
        "is_active": True,
    }
    response = await authenticated_client.post("/webhooks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == payload["url"]
    assert data["event_type"] == payload["event_type"]
    assert "id" in data


@pytest.mark.integration
async def test_api_list_webhooks(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test GET /webhooks lists registered subscriptions."""
    response = await authenticated_client.get("/webhooks")
    assert response.status_code == 200
    data = response.json()
    assert "webhooks" in data or "items" in data
    assert "total" in data


@pytest.mark.integration
async def test_api_test_webhook_dispatch(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /webhooks/test/{id} triggers a test ping with signature."""
    # First create webhook
    payload = {
        "url": "https://httpbin.org/post",
        "secret": "whsec_test_secret_123",
        "event_type": "*",
        "is_active": True,
    }
    create_res = await authenticated_client.post("/webhooks", json=payload)
    webhook_id = create_res.json()["id"]

    # Mock dispatch to prevent real external network calls
    with patch("app.core.webhook.dispatch_webhook_request", new_callable=AsyncMock) as mock_dispatch:
        mock_dispatch.return_value = {"status": "dispatched", "status_code": 200, "success": True}
        test_res = await authenticated_client.post(f"/webhooks/test/{webhook_id}")
        assert test_res.status_code == 200
        data = test_res.json()
        assert data["success"] is True


@pytest.mark.integration
async def test_api_delete_webhook(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test DELETE /webhooks/{id} removes subscription."""
    payload = {
        "url": "https://example.com/delete-target",
        "secret": "whsec_secret_to_delete",
        "event_type": "*",
        "is_active": True,
    }
    create_res = await authenticated_client.post("/webhooks", json=payload)
    webhook_id = create_res.json()["id"]

    del_res = await authenticated_client.delete(f"/webhooks/{webhook_id}")
    assert del_res.status_code == 200
