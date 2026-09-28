"""Unit tests for cryptographic security, password hashing, JWTs, and API keys."""
import hashlib
import uuid
import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.webhook import generate_webhook_signature
from tests.utils import create_expired_jwt, create_test_jwt


@pytest.mark.unit
def test_password_hashing():
    """Test bcrypt password hashing and verification."""
    password = "MyComplexPassword#2026!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


@pytest.mark.unit
def test_jwt_lifecycle():
    """Test standard access and refresh token encoding and decoding."""
    uid = str(uuid.uuid4())
    token = create_access_token(data={"sub": uid, "username": "jwt_user"})

    payload = verify_token(token, expected_type="access")
    assert payload["sub"] == uid
    assert payload["username"] == "jwt_user"
    assert payload["type"] == "access"


@pytest.mark.unit
def test_jwt_expired_token():
    """Test that expired JWT raises 401 HTTPException."""
    expired_token = create_expired_jwt()
    with pytest.raises(HTTPException) as exc_info:
        verify_token(expired_token, expected_type="access")
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.unit
def test_jwt_tampered_signature():
    """Test that signature tampering raises 401 HTTPException."""
    uid = str(uuid.uuid4())
    token = create_access_token(data={"sub": uid})
    tampered_token = token[:-5] + "XXXXX"

    with pytest.raises(HTTPException) as exc_info:
        verify_token(tampered_token, expected_type="access")
    assert exc_info.value.status_code == 401


@pytest.mark.unit
def test_webhook_signature_generation():
    """Test HMAC-SHA256 signature generation and deterministic matching."""
    secret = "test_webhook_secret_key"
    payload = b'{"event": "review.completed", "score": 90}'

    sig1 = generate_webhook_signature(payload, secret)
    sig2 = generate_webhook_signature(payload, secret)

    assert sig1 == sig2
    # generate_webhook_signature returns a plain 64-char hex digest (no sha256= prefix)
    assert len(sig1) == 64
    assert all(c in "0123456789abcdef" for c in sig1)

    # Verify signature calculation directly
    import hmac
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert sig1 == expected
