"""Security tests for injection attacks, malformed payloads, and input sanitization."""
import httpx
import pytest


@pytest.mark.security
async def test_sql_injection_attempt_in_login(client: httpx.AsyncClient):
    """Test SQL injection string in login parameters does not compromise database."""
    payload = {
        "username_or_email": "' OR '1'='1",
        "password": "' OR '1'='1",
    }
    response = await client.post("/auth/login", json=payload)
    # Must fail securely with 401 Unauthorized, never 500 or 200
    assert response.status_code == 401


@pytest.mark.security
async def test_xss_payload_in_review_code(client: httpx.AsyncClient):
    """Test XSS script injection in code review payload is handled safely."""
    xss_code = '<script>alert("XSS")</script>\ndef test():\n    return True\n'
    payload = {
        "code": xss_code,
        "language": "python",
        "filename": "<script>alert(1)</script>.py",
    }
    response = await client.post("/review/code", json=payload)
    assert response.status_code == 200
    # Response is structured JSON, ensuring script cannot be executed
    assert "scores" in response.json()


@pytest.mark.security
async def test_malformed_json_body(client: httpx.AsyncClient):
    """Test unparseable JSON returns 422 Unprocessable Entity."""
    response = await client.post(
        "/auth/register",
        content=b'{"username": "bad_json", "email": }',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in (400, 422)


@pytest.mark.security
async def test_missing_required_fields_422(client: httpx.AsyncClient):
    """Test missing required schema fields triggers Pydantic 422 validation error."""
    payload = {"username": "missing_fields_user"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    errors = data.get("detail") or data.get("errors", [])
    assert any("email" in err["loc"] for err in errors)
