"""Integration tests for Analytics API endpoints."""
import httpx
import pytest

from app.models.review import Review


@pytest.mark.integration
async def test_api_analytics_overview(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/overview endpoint."""
    response = await authenticated_client.get("/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data


@pytest.mark.integration
async def test_api_analytics_scores(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/scores endpoint."""
    response = await authenticated_client.get("/analytics/scores")
    assert response.status_code == 200


@pytest.mark.integration
async def test_api_analytics_issues(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/issues endpoint."""
    response = await authenticated_client.get("/analytics/issues")
    assert response.status_code == 200
    data = response.json()
    assert "category_breakdown" in data or "severity_distribution" in data or "total_issues" in data


@pytest.mark.integration
async def test_api_analytics_security(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/security endpoint."""
    response = await authenticated_client.get("/analytics/security")
    assert response.status_code == 200


@pytest.mark.integration
async def test_api_analytics_heatmap(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/heatmap endpoint."""
    response = await authenticated_client.get("/analytics/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "heatmap" in data or "days_recorded" in data or "total_reviews_year" in data


@pytest.mark.integration
async def test_api_analytics_export_json(
    authenticated_client: httpx.AsyncClient,
    sample_review: Review,
):
    """Test GET /analytics/export?format=json endpoint."""
    response = await authenticated_client.get("/analytics/export?format=json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
