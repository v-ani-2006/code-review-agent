"""User entity fixtures for authentication and role-based test scenarios."""
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.factories.user_factory import UserFactory


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create and persist standard active user."""
    return await UserFactory.create(
        db=db_session,
        username="standard_tester",
        email="standard_tester@example.com",
        password="TestPass123!",
        is_active=True,
        is_admin=False,
    )


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """Create and persist active administrator user."""
    return await UserFactory.create(
        db=db_session,
        username="admin_tester",
        email="admin_tester@example.com",
        password="AdminPass123!",
        is_active=True,
        is_admin=True,
    )


@pytest_asyncio.fixture(scope="function")
async def inactive_user(db_session: AsyncSession) -> User:
    """Create and persist deactivated user account."""
    return await UserFactory.create(
        db=db_session,
        username="inactive_tester",
        email="inactive_tester@example.com",
        password="TestPass123!",
        is_active=False,
        is_admin=False,
    )
