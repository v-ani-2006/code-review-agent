"""Comprehensive Gemini AI Provider Mock for deterministic and offline testing."""
import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, patch

from app.ai.providers.base import AIAnalysisContext, AIProviderResponse, BaseAIProvider


class MockGeminiProvider(BaseAIProvider):
    """Deterministic offline Gemini mock provider supporting success and failure simulation."""

    def __init__(
        self,
        mode: str = "success",
        delay: float = 0.0,
        model: str = "gemini-2.5-flash",
    ):
        self.mode = mode
        self.delay = delay
        self.model = model
        self.call_history: List[Dict[str, Any]] = []

    async def _simulate_latency(self) -> None:
        if self.delay > 0:
            await asyncio.sleep(self.delay)

    def _check_failure_mode(self) -> None:
        if self.mode == "timeout":
            raise asyncio.TimeoutError("Gemini API request timed out after 60s")
        elif self.mode == "quota_exceeded":
            raise RuntimeError("Gemini API error 429: Resource has been exhausted (quota exceeded)")
        elif self.mode == "unavailable":
            raise RuntimeError("Gemini API error 503: The service is currently unavailable")
        elif self.mode == "malformed":
            pass  # Handled in responses returning invalid text

    async def _generate_response(self, prompt: str) -> AIProviderResponse:
        self.call_history.append({"method": "_generate_response", "prompt": prompt})
        await self._simulate_latency()
        self._check_failure_mode()

        payload = {
            "module_overview": "Mocked module architecture and design overview.",
            "classes": [
                {
                    "name": "SampleClass",
                    "docstring": "Sample class documentation.",
                    "attributes": [{"name": "id", "type": "str", "description": "Identifier"}],
                }
            ],
            "functions": [
                {
                    "name": "sample_function",
                    "signature": "x: int -> int",
                    "docstring": "Sample function docstring.",
                    "parameters": [{"name": "x", "type": "int", "default": None, "description": "Input value"}],
                    "return_type": "int",
                    "return_description": "Doubled value",
                    "raises": [],
                    "example": "sample_function(5)",
                }
            ],
            "docstring": '"""Mocked docstring representation."""',
            "refactored_code": "# Refactored version\ndef clean_code():\n    return True\n",
            "changelog": "# Changelog\n- Added improvements and type annotations.\n",
            "architecture_summary": "Clean layered architecture with decoupled services.",
            "test_code": "import pytest\n\ndef test_mock_success():\n    assert True\n",
            "summary": "High quality implementation meeting all architectural criteria.",
            "score": 90,
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.05,
            success=True,
        )

    async def review_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "review_code", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        if self.mode == "malformed":
            return AIProviderResponse(
                raw_text="This is not valid JSON and has no structured blocks at all.",
                parsed_json=None,
                model_used=self.model,
                processing_time=0.05,
                success=True,
            )

        payload = {
            "score": 92,
            "summary": "The code is well-structured and follows Python best practices with clean type annotations.",
            "issues": [
                {
                    "type": "style",
                    "severity": "low",
                    "line": 10,
                    "message": "Function docstring could include additional return type details.",
                    "suggestion": "Add explicit return annotation description.",
                }
            ],
            "strengths": [
                "Strict typing with type annotations",
                "Explicit None check on empty sequences",
            ],
            "recommendations": [
                "Consider caching results for repeated inputs.",
            ],
            "security_analysis": "Security analysis: risk_level=low, no vulnerabilities found.",
        }

        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.08,
            success=True,
        )

    async def explain_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "explain_code", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        payload = {
            "overview": "This Python module provides helper routines for numerical calculation and string formatting.",
            "beginner_explanation": "This Python module provides helper routines for numerical calculation and string formatting.",
            "execution_flow": [
                "1. Validates input sequences.",
                "2. Computes the arithmetic sum.",
                "3. Returns formatted result.",
            ],
            "complexity_summary": "O(N) time complexity and O(1) auxiliary space complexity.",
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.06,
            success=True,
        )

    async def optimize_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "optimize_code", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        payload = {
            "optimized_code": context.source_code.strip() + "\n# Optimized with pre-computed length\n",
            "performance_improvements": [
                "Replaced repeated len() calls with local cached variable.",
                "Utilized generator expression to minimize memory allocation.",
            ],
            "optimizations": [
                "Replaced repeated len() calls with local cached variable.",
                "Utilized generator expression to minimize memory allocation.",
            ],
            "time_complexity": "O(N)",
            "memory_complexity": "O(1)",
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.09,
            success=True,
        )

    async def fix_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "fix_code", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        payload = {
            "bugs_found": [
                {
                    "line": 5,
                    "description": "Potential ZeroDivisionError when sequence is empty.",
                    "severity": "high",
                }
            ],
            "identified_bugs": [
                {
                    "line": 5,
                    "description": "Potential ZeroDivisionError when sequence is empty.",
                    "severity": "high",
                }
            ],
            "fixed_code": "# Guard added\n" + context.source_code,
            "corrected_code": "# Guard added\n" + context.source_code,
            "explanation": "Added zero-length list guard check prior to division.",
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.07,
            success=True,
        )

    async def generate_documentation(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "generate_documentation", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        payload = {
            "module_docstring": "Enterprise utility routines for CodePilot AI service with comprehensive docstrings.",
            "documented_code": f'"""Module documentation."""\n\n{context.source_code}',
            "functions": [
                {
                    "name": "calculate_average",
                    "docstring": "Computes arithmetic mean of floating-point sequences.",
                }
            ],
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.08,
            success=True,
        )

    async def generate_tests(self, context: AIAnalysisContext) -> AIProviderResponse:
        self.call_history.append({"method": "generate_tests", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()

        test_code = """import pytest

def test_success_case():
    assert True

def test_boundary_case():
    assert 1 + 1 == 2
"""
        payload = {
            "test_code": test_code,
            "framework": "pytest",
            "test_framework": "pytest",
            "coverage_estimate": 95,
        }
        return AIProviderResponse(
            raw_text=str(payload),
            parsed_json=payload,
            model_used=self.model,
            processing_time=0.08,
            success=True,
        )

    async def generate_summary(self, context: AIAnalysisContext) -> str:
        self.call_history.append({"method": "generate_summary", "context": context})
        await self._simulate_latency()
        self._check_failure_mode()
        return "Deterministic AI executive summary: high quality code with low complexity."

    async def get_available_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": "gemini",
            "model": self.model,
            "configured": True,
            "status": "ready" if self.mode == "success" else "error",
            "timeout_seconds": 60,
            "max_retries": 3,
        }
