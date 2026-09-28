"""AI, Redis, and Webhook fixtures and monkeypatchers."""
from typing import Generator
from unittest.mock import patch
import pytest

from tests.mocks.gemini_mock import MockGeminiProvider
from tests.mocks.redis_mock import MockRedisClient
from tests.mocks.webhook_mock import MockWebhookReceiver


@pytest.fixture
def mock_gemini() -> MockGeminiProvider:
    """Deterministic MockGeminiProvider instance in success mode."""
    return MockGeminiProvider(mode="success")


@pytest.fixture
def mock_gemini_failure() -> MockGeminiProvider:
    """MockGeminiProvider instance simulating quota exceeded error."""
    return MockGeminiProvider(mode="quota_exceeded")


@pytest.fixture(autouse=True)
def patch_gemini_provider(mock_gemini: MockGeminiProvider) -> Generator[MockGeminiProvider, None, None]:
    """Globally patch get_ai_provider across all services to prevent external Gemini network requests."""
    with patch("app.ai.providers.provider_factory.get_ai_provider", return_value=mock_gemini), \
         patch("app.ai.ai_service.get_ai_provider", return_value=mock_gemini), \
         patch("app.ai.get_ai_provider", return_value=mock_gemini):
        yield mock_gemini


@pytest.fixture
def mock_redis() -> MockRedisClient:
    """MockRedisClient instance for isolated cache testing."""
    return MockRedisClient()


@pytest.fixture(autouse=True)
def patch_redis_client(mock_redis: MockRedisClient) -> Generator[MockRedisClient, None, None]:
    """Globally patch Redis client across all tests to prevent network attempts.
    
    CacheService doesn't hold a .redis attribute — it calls redis_manager.get_client()
    on each operation. So we patch the manager's get_client method and client attribute.
    """
    with patch("app.core.cache.redis_manager.client", mock_redis), \
         patch("app.core.cache.redis_manager.get_client", return_value=mock_redis):
        yield mock_redis



@pytest.fixture
def mock_webhook() -> MockWebhookReceiver:
    """MockWebhookReceiver instance for outbound delivery interception."""
    return MockWebhookReceiver(response_status=200)
