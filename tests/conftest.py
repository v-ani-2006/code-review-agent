"""Global pytest configuration, fixture imports, and HTTP client wiring."""
from pathlib import Path
import sys
from typing import AsyncGenerator

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx
from httpx import ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
# Disable slowapi rate limiting during test executions to prevent throttling or Redis connection attempts
limiter.enabled = False

from app.db.session import get_db
from app.main import app


# Import all fixtures so pytest discovers them globally
from tests.fixtures import (
    admin_auth_headers,
    admin_token,
    admin_user,
    api_key_headers,
    auth_headers,
    db_session,
    inactive_user,
    isolated_upload_dir,
    mock_gemini,
    mock_gemini_failure,
    mock_redis,
    mock_webhook,
    patch_gemini_provider,
    patch_redis_client,
    sample_review,

    sample_reviews_list,
    sample_task,
    sample_upload,
    test_user,
    user_token,
)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an asynchronous HTTP client wired to the FastAPI application with an isolated DB session."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    client: httpx.AsyncClient,
    auth_headers: dict,
) -> httpx.AsyncClient:
    """Async HTTP client pre-configured with active user Bearer authentication."""
    client.headers.update(auth_headers)
    return client


@pytest_asyncio.fixture(scope="function")
async def admin_client(
    client: httpx.AsyncClient,
    admin_auth_headers: dict,
) -> httpx.AsyncClient:
    """Async HTTP client pre-configured with administrator Bearer authentication."""
    client.headers.update(admin_auth_headers)
    return client
