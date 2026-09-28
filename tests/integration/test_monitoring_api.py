"""Integration tests for Monitoring, Diagnostics, and Health endpoints."""
import httpx
import pytest


@pytest.mark.integration
async def test_api_health(client: httpx.AsyncClient):
    """Test GET /health subsystem health probe."""
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


@pytest.mark.integration
async def test_api_monitoring_health(client: httpx.AsyncClient):
    """Test GET /monitoring/health endpoint."""
    response = await client.get("/monitoring/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "components" in data or "database" in data or "status" in data


@pytest.mark.integration
async def test_api_monitoring_status(client: httpx.AsyncClient):
    """Test GET /monitoring/status ping latency probe."""
    response = await client.get("/monitoring/status")
    assert response.status_code == 200
    data = response.json()
    assert "application" in data or "app_name" in data



@pytest.mark.integration
async def test_api_monitoring_system(client: httpx.AsyncClient):
    """Test GET /monitoring/system hardware telemetry endpoint."""
    response = await client.get("/monitoring/system")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_cores" in data
    assert "memory_total_mb" in data


@pytest.mark.integration
async def test_api_metrics(client: httpx.AsyncClient):
    """Test GET /metrics Prometheus scrape format."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
