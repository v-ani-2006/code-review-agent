"""Integration tests for Review API endpoints."""
import httpx
import pytest

from app.models.user import User


@pytest.mark.integration
async def test_api_review_code_unauthenticated(client: httpx.AsyncClient):
    """Test POST /review/code allows anonymous analysis without saving."""
    payload = {
        "code": "def hello():\n    return 'world'\n",
        "language": "python",
        "filename": "hello.py",
    }
    response = await client.post("/review/code", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scores"]["overall"] >= 80
    assert data["metadata"].get("review_id") is None


@pytest.mark.integration
async def test_api_review_code_authenticated(
    authenticated_client: httpx.AsyncClient,
    test_user: User,
):
    """Test POST /review/code persists review when user is authenticated."""
    payload = {
        "code": "def calculate_sum(items):\n    return sum(items)\n",
        "language": "python",
        "filename": "calc.py",
    }
    response = await authenticated_client.post("/review/code", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"].get("review_id") is not None
    assert data["metadata"].get("user_id") == str(test_user.id)


@pytest.mark.integration
async def test_api_review_text_snippet(client: httpx.AsyncClient):
    """Test POST /review/text lightweight analysis endpoint."""
    payload = {"code": "x = 10\ny = 20\nprint(x + y)\n"}
    response = await client.post("/review/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scores" in data


@pytest.mark.integration
async def test_api_review_languages(client: httpx.AsyncClient):
    """Test GET /review/languages metadata endpoint."""
    response = await client.get("/review/languages")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0


@pytest.mark.integration
async def test_api_review_rules(client: httpx.AsyncClient):
    """Test GET /review/rules definitions endpoint."""
    response = await client.get("/review/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
