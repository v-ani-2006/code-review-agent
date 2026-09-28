"""AI static code analysis and Gemini reasoning package."""

from app.ai.ai_service import ai_service
from app.ai.analyzer import analyze_code
from app.ai.constants import ANALYSIS_RULES, SUPPORTED_LANGUAGES, Category, Severity
from app.ai.models import AIAnalysisContext, AIProviderResponse
from app.ai.providers import BaseAIProvider, GeminiProvider, get_ai_provider
from app.ai.report import build_review_report

__all__ = [
    "ai_service",
    "analyze_code",
    "build_review_report",
    "Severity",
    "Category",
    "SUPPORTED_LANGUAGES",
    "ANALYSIS_RULES",
    "AIAnalysisContext",
    "AIProviderResponse",
    "BaseAIProvider",
    "GeminiProvider",
    "get_ai_provider",
]
