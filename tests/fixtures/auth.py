"""Authentication and token header fixtures."""
from typing import Dict
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from app.models.user import User
from tests.factories.additional_factories import APIKeyFactory
from tests.utils import create_test_jwt


@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate valid JWT access token for test_user."""
    return create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "email": test_user.email}
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate valid JWT access token for admin_user."""
    return create_access_token(
        data={"sub": str(admin_user.id), "username": admin_user.username, "email": admin_user.email}
    )


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    """Header dictionary with standard Bearer authorization."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_auth_headers(admin_token: str) -> Dict[str, str]:
    """Header dictionary with administrator Bearer authorization."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def api_key_headers(test_user: User, db_session: AsyncSession) -> Dict[str, str]:
    """Header dictionary with authenticated X-API-Key header."""
    raw_key = "cp_live_test_fixture_key_1234567890abcdef"
    await APIKeyFactory.create(
        db=db_session,
        user_id=test_user.id,
        name="Fixture Key",
        raw_key=raw_key,
        is_active=True,
        permissions=["*"],
    )
    return {"X-API-Key": raw_key}
