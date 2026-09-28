"""Integration tests for AI Review and reasoning endpoints."""
import httpx
import pytest

from app.models.user import User

SAMPLE_CODE = "def add(x: int, y: int) -> int:\n    return x + y\n"


@pytest.mark.integration
async def test_api_ai_review(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /ai/review with authenticated client."""
    payload = {
        "code": SAMPLE_CODE,
        "language": "python",
        "filename": "math_util.py",
    }
    response = await authenticated_client.post("/ai/review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "review" in data
    assert data["review"]["summary"] is not None
    assert data["static_report"] is not None


@pytest.mark.integration
async def test_api_ai_explain(client: httpx.AsyncClient):
    """Test POST /ai/explain code reasoning endpoint."""
    payload = {"code": SAMPLE_CODE, "language": "python"}
    response = await client.post("/ai/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data or "explanation" in data


@pytest.mark.integration
async def test_api_ai_optimize(client: httpx.AsyncClient):
    """Test POST /ai/optimize code optimization endpoint."""
    payload = {"code": SAMPLE_CODE, "language": "python"}
    response = await client.post("/ai/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data or "optimization" in data


@pytest.mark.integration
async def test_api_ai_fix(client: httpx.AsyncClient):
    """Test POST /ai/fix bug correction endpoint."""
    payload = {"code": SAMPLE_CODE, "language": "python"}
    response = await client.post("/ai/fix", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data or "bug_fix" in data


@pytest.mark.integration
async def test_api_ai_docs(client: httpx.AsyncClient):
    """Test POST /ai/docs documentation endpoint."""
    payload = {"code": SAMPLE_CODE, "language": "python"}
    response = await client.post("/ai/docs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data or "documentation" in data


@pytest.mark.integration
async def test_api_ai_tests(client: httpx.AsyncClient):
    """Test POST /ai/tests pytest suite generation endpoint."""
    payload = {"code": SAMPLE_CODE, "language": "python"}
    response = await client.post("/ai/tests", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data or "tests" in data


@pytest.mark.integration
async def test_api_ai_models(client: httpx.AsyncClient):
    """Test GET /ai/models model discovery endpoint."""
    response = await client.get("/ai/models")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    models = data.get("available_models") or data.get("models") or []
    assert len(models) > 0


@pytest.mark.integration
async def test_api_ai_status(client: httpx.AsyncClient):
    """Test GET /ai/status provider readiness probe."""
    response = await client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data
