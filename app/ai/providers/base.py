from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.ai.models import AIAnalysisContext, AIProviderResponse


class BaseAIProvider(ABC):
    """Abstract base class defining the contract for all AI reasoning providers."""

    @abstractmethod
    async def review_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Perform an in-depth semantic code review enriched with static AST findings."""
        pass

    @abstractmethod
    async def explain_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate intuitive explanations, execution flows, and line-by-line breakdowns."""
        pass

    @abstractmethod
    async def optimize_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate algorithmically and Pythonically optimized source code."""
        pass

    @abstractmethod
    async def fix_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Identify logic/runtime bugs and provide corrected source code."""
        pass

    @abstractmethod
    async def generate_documentation(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate comprehensive docstrings, parameter guides, and usage examples."""
        pass

    @abstractmethod
    async def generate_tests(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate a complete pytest test suite covering unit cases, edge cases, and mocks."""
        pass

    @abstractmethod
    async def generate_summary(self, context: AIAnalysisContext) -> str:
        """Generate a concise executive summary for a code review."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Return the list of available model identifiers for this provider."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a liveness and connectivity verification for the provider."""
        pass
