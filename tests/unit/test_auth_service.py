"""Unit tests for AuthService logic and credential lifecycle."""
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import auth_service
from tests.factories.user_factory import UserFactory


@pytest.mark.unit
async def test_register_user_success(db_session: AsyncSession):
    """Test successful user registration with password hashing."""
    reg_data = RegisterRequest(
        username="new_coder",
        email="new_coder@example.com",
        password="SecurePass123!",
        full_name="New Coder",
    )
    user = await auth_service.register_user(db_session, reg_data)

    assert user is not None
    assert user.username == "new_coder"
    assert user.email == "new_coder@example.com"
    assert user.password_hash != "SecurePass123!"
    assert verify_password("SecurePass123!", user.password_hash)


@pytest.mark.unit
async def test_register_duplicate_username(db_session: AsyncSession, test_user: User):
    """Test registration failure when username already exists."""
    reg_data = RegisterRequest(
        username=test_user.username,
        email="unique_email@example.com",
        password="SecurePass123!",
    )
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(db_session, reg_data)
    assert exc_info.value.status_code == 409
    assert "username already exists" in exc_info.value.detail.lower()


@pytest.mark.unit
async def test_register_duplicate_email(db_session: AsyncSession, test_user: User):
    """Test registration failure when email already exists."""
    reg_data = RegisterRequest(
        username="unique_username_99",
        email=test_user.email,
        password="SecurePass123!",
    )
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(db_session, reg_data)
    assert exc_info.value.status_code == 409
    assert "email address already exists" in exc_info.value.detail.lower()


@pytest.mark.unit
async def test_authenticate_user_success(db_session: AsyncSession, test_user: User):
    """Test authentication by username and by email with correct password."""
    # Authenticate by username
    user_by_name = await auth_service.authenticate_user(
        db_session, test_user.username, "TestPass123!"
    )
    assert user_by_name.id == test_user.id

    # Authenticate by email
    user_by_email = await auth_service.authenticate_user(
        db_session, test_user.email, "TestPass123!"
    )
    assert user_by_email.id == test_user.id


@pytest.mark.unit
async def test_authenticate_user_invalid_password(db_session: AsyncSession, test_user: User):
    """Test authentication failure with incorrect password."""
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(
            db_session, test_user.username, "WrongPassword!"
        )
    assert exc_info.value.status_code == 401
    assert "incorrect" in exc_info.value.detail.lower()


@pytest.mark.unit
async def test_authenticate_user_not_found(db_session: AsyncSession):
    """Test authentication failure for non-existent user."""
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(
            db_session, "non_existent_user_999", "AnyPass123!"
        )
    assert exc_info.value.status_code == 401


@pytest.mark.unit
async def test_issue_tokens(test_user: User):
    """Test issuance of access and refresh tokens."""
    tokens = auth_service.generate_tokens(test_user)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"
    assert tokens.expires_in > 0

