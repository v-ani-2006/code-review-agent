"""Integration tests for History API endpoints."""
import uuid
import httpx
import pytest

from app.models.review import Review
from app.models.user import User


@pytest.mark.integration
async def test_api_list_history(
    authenticated_client: httpx.AsyncClient,
    test_user: User,
    sample_review: Review,
):
    """Test GET /history lists user review records."""
    response = await authenticated_client.get("/history")
    assert response.status_code == 200
    data = response.json()
    total = data.get("total") or data.get("meta", {}).get("total_items", 0)
    assert total >= 1
    assert any(item["id"] == str(sample_review.id) for item in data["items"])


@pytest.mark.integration
async def test_api_get_history_detail(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /history/{id} retrieves specific review details."""
    response = await authenticated_client.get(f"/history/{sample_review.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_review.id)
    assert data["filename"] == sample_review.filename


@pytest.mark.integration
async def test_api_get_history_not_found(authenticated_client: httpx.AsyncClient):
    """Test GET /history/{id} returns 404 for non-existent UUID."""
    fake_id = uuid.uuid4()
    response = await authenticated_client.get(f"/history/{fake_id}")
    assert response.status_code == 404


@pytest.mark.integration
async def test_api_toggle_favorite(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test PATCH /history/{id}/favorite toggles favorite status."""
    response = await authenticated_client.patch(f"/history/{sample_review.id}/favorite")
    assert response.status_code == 200
    data = response.json()
    assert "favorite" in data


@pytest.mark.integration
async def test_api_soft_delete_and_restore(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test DELETE /history/{id} and subsequent restore."""
    del_res = await authenticated_client.delete(f"/history/{sample_review.id}")
    assert del_res.status_code == 200

    restore_res = await authenticated_client.post(f"/history/{sample_review.id}/restore")
    assert restore_res.status_code == 200


@pytest.mark.integration
async def test_api_history_timeline(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /history/timeline returns aggregated timeline."""
    response = await authenticated_client.get("/history/timeline")
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
