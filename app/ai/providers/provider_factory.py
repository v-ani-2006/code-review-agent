from functools import lru_cache
from typing import Dict, Optional, Type
from app.ai.providers.base import BaseAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.core.logging import logger

# Registry of supported AI providers
PROVIDER_REGISTRY: Dict[str, Type[BaseAIProvider]] = {
    "gemini": GeminiProvider,
    "google": GeminiProvider,
}

_provider_instances: Dict[str, BaseAIProvider] = {}


class ProviderFactory:
    """Factory creating and managing AI provider instances."""

    @classmethod
    def get_provider(
        cls,
        provider_type: str = "gemini",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> BaseAIProvider:
        """Instantiate or retrieve a configured AI provider."""
        normalized = provider_type.lower().strip()
        provider_cls = PROVIDER_REGISTRY.get(normalized)

        if not provider_cls:
            logger.warning("Unknown AI provider '%s' requested; falling back to 'gemini'", provider_type)
            provider_cls = GeminiProvider

        # Cache instance key
        cache_key = f"{normalized}:{model or 'default'}"
        if cache_key not in _provider_instances or api_key is not None:
            instance = provider_cls(
                api_key=api_key,
                model=model,
                timeout=timeout,
                max_retries=max_retries,
            )
            if api_key is None:
                _provider_instances[cache_key] = instance
            return instance

        return _provider_instances[cache_key]

    @classmethod
    def register_provider(cls, name: str, provider_cls: Type[BaseAIProvider]) -> None:
        """Register a new provider class for future extension."""
        PROVIDER_REGISTRY[name.lower().strip()] = provider_cls
        logger.info("Registered custom AI provider: '%s'", name)


def get_ai_provider(
    provider_type: str = "gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseAIProvider:
    """Convenience helper to obtain an AI provider instance."""
    return ProviderFactory.get_provider(
        provider_type=provider_type,
        model=model,
        api_key=api_key,
    )
