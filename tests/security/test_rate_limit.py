"""Security tests for client identification, rate limiting, and 429 response handling."""
import pytest
from starlette.requests import Request

from app.core.limiter import custom_rate_limit_exceeded_handler, get_client_identifier


@pytest.mark.security
def test_get_client_identifier_from_api_key():
    """Verify that X-API-Key is prioritized for client rate identification."""
    scope = {
        "type": "http",
        "headers": [(b"x-api-key", b"cp_live_test_key_1234567890")],
    }
    req = Request(scope)
    ident = get_client_identifier(req)
    assert ident.startswith("apikey:cp_live_test")


@pytest.mark.security
def test_get_client_identifier_from_bearer():
    """Verify that Authorization Bearer is extracted when no API key is present."""
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz")],
    }
    req = Request(scope)
    ident = get_client_identifier(req)
    assert ident.startswith("token:eyJhbGciOiJIUzI1")


@pytest.mark.security
def test_get_client_identifier_from_ip():
    """Verify that client IP is used as fallback when no headers exist."""
    scope = {
        "type": "http",
        "client": ("192.168.1.100", 54321),
        "headers": [],
    }
    req = Request(scope)
    ident = get_client_identifier(req)
    assert ident == "ip:192.168.1.100"


@pytest.mark.security
def test_custom_rate_limit_handler():
    """Verify custom 429 response conforms to platform standard and includes Retry-After header."""
    scope = {"type": "http", "method": "GET", "path": "/test", "headers": []}
    req = Request(scope)

    class MockRateLimitExceeded(Exception):
        detail = "15 per 1 minute"

    res = custom_rate_limit_exceeded_handler(req, MockRateLimitExceeded())
    assert res.status_code == 429
    assert "Retry-After" in res.headers
    assert res.headers["Retry-After"] == "60"
