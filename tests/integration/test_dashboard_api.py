"""Integration tests for Developer Dashboard API endpoints."""
import httpx
import pytest

from app.models.review import Review
from app.models.user import User


@pytest.mark.integration
async def test_api_dashboard_overview(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /dashboard/overview endpoint."""
    response = await authenticated_client.get("/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "average_score" in data


@pytest.mark.integration
async def test_api_dashboard_activity(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /dashboard/activity endpoint."""
    response = await authenticated_client.get("/dashboard/activity")
    assert response.status_code == 200
    data = response.json()
    assert "reviews_this_week" in data or "this_week" in str(data)
    assert "reviews_this_month" in data or "this_month" in str(data)


@pytest.mark.integration
async def test_api_dashboard_streak(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /dashboard/streak endpoint."""
    response = await authenticated_client.get("/dashboard/streak")
    assert response.status_code == 200
    data = response.json()
    assert "current_streak" in data or "current_streak_days" in data
    assert "longest_streak" in data or "longest_streak_days" in data


@pytest.mark.integration
async def test_api_dashboard_progress(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /dashboard/progress endpoint."""
    response = await authenticated_client.get("/dashboard/progress")
    assert response.status_code == 200
    data = response.json()
    assert "progression" in data


@pytest.mark.integration
async def test_api_dashboard_insights(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /dashboard/insights endpoint."""
    response = await authenticated_client.get("/dashboard/insights")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
