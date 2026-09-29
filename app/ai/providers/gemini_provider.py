import asyncio
import time
from typing import Any, Dict, List, Optional
import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.ai.models import AIAnalysisContext, AIProviderResponse
from app.ai.parser import extract_json_fragment, normalize_whitespace
from app.ai.prompts import (
    build_bugfix_prompt,
    build_documentation_prompt,
    build_explain_prompt,
    build_optimize_prompt,
    build_review_prompt,
    build_unittest_prompt,
)
from app.ai.providers.base import BaseAIProvider
from app.core.config import settings
from app.core.logging import logger

AVAILABLE_GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI reasoning provider implementation.

    Utilizes asynchronous HTTP client with automatic model fallback across active
    Gemini endpoints, timeout handling, and JSON parsing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-3.1-flash-lite"
        self.timeout = timeout or settings.AI_TIMEOUT_SECONDS or 60
        self.max_retries = max_retries or settings.AI_MAX_RETRIES or 3
        self._http_client: Optional[httpx.AsyncClient] = None
        self._active_model_used: str = self.model

    def _get_http_client(self) -> httpx.AsyncClient:
        """Get or initialize reusable HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return self._http_client

    async def close(self) -> None:
        """Gracefully close HTTP client."""
        if self._http_client is not None and not self._http_client.is_closed:
            await self._http_client.aclose()

    @property
    def current_api_key(self) -> Optional[str]:
        """Dynamically resolve the latest API key from instance, settings, os.environ, or .env file."""
        if self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here":
            return self.api_key.strip()
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
            return settings.GEMINI_API_KEY.strip()
        import os
        env_val = os.getenv("GEMINI_API_KEY")
        if env_val and env_val.strip() and env_val != "your_gemini_api_key_here":
            return env_val.strip()
        try:
            from dotenv import dotenv_values
            vals = dotenv_values(".env")
            file_val = vals.get("GEMINI_API_KEY")
            if file_val and file_val.strip() and file_val != "your_gemini_api_key_here":
                return file_val.strip()
        except Exception:
            pass
        return None

    def _sanitize_code(self, code: str, max_lines: int = 5000) -> str:
        """Ensure source code payload does not exceed length limits."""
        lines = code.splitlines()
        if len(lines) > max_lines:
            logger.warning("Code payload truncated from %d to %d lines", len(lines), max_lines)
            return "\n".join(lines[:max_lines]) + f"\n\n# ... [Truncated: {len(lines) - max_lines} lines omitted] ..."
        return code

    async def _execute_with_retry(self, prompt: str) -> str:
        """Execute Gemini API generation request with multi-model fallback."""
        active_key = self.current_api_key
        if not active_key or active_key.strip() == "" or active_key == "your_gemini_api_key_here":
            raise ValueError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment or .env file."
            )

        # Candidate models list with fallback priority
        candidate_models = [self.model, "gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash"]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        client = self._get_http_client()
        last_exception = None

        for target_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={active_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.95,
                },
            }

            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info("Executing Gemini request (Attempt %d) to model '%s'", attempt, target_model)
                    resp = await client.post(url, json=payload)

                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                self._active_model_used = target_model
                                return parts[0]["text"]
                        raise RuntimeError(f"Malformed response from Gemini model {target_model}")

                    # 404 means model deprecated/not available; 429 quota; 503 high demand -> fallback to next candidate model
                    if resp.status_code in (404, 429, 503):
                        logger.warning(
                            "Model '%s' returned status %d (%s). Falling back to next model candidate.",
                            target_model,
                            resp.status_code,
                            resp.text[:100],
                        )
                        last_exception = RuntimeError(f"Model {target_model} returned {resp.status_code}")
                        break  # Break inner loop to try next model candidate immediately

                    if resp.status_code in (500, 502, 504):
                        logger.warning("Transient error %d on model '%s'. Retrying attempt %d...", resp.status_code, target_model, attempt)
                        await asyncio.sleep(1.5 * attempt)
                        continue

                    error_detail = resp.text
                    logger.error("Gemini API error %d: %s", resp.status_code, error_detail)
                    last_exception = RuntimeError(f"Gemini API returned status {resp.status_code}: {error_detail}")
                    break

                except httpx.RequestError as exc:
                    logger.warning("Network request error on '%s': %s", target_model, str(exc))
                    last_exception = exc
                    await asyncio.sleep(1.0)

        if last_exception:
            raise last_exception
        raise RuntimeError("Gemini failed to return text content after all fallback model attempts.")

    async def _generate_response(self, prompt: str) -> AIProviderResponse:
        """Internal helper to time, execute, and package generation."""
        start_time = time.perf_counter()
        sanitized_prompt = prompt
        try:
            logger.info("AI request started | Preferred Model: %s", self.model)
            raw_text = await self._execute_with_retry(sanitized_prompt)
            duration = round(time.perf_counter() - start_time, 4)
            logger.info("AI request completed in %.4fs | Model: %s", duration, self._active_model_used)

            parsed = extract_json_fragment(raw_text)
            return AIProviderResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_used=self._active_model_used,
                processing_time=duration,
                success=True,
            )
        except Exception as exc:
            duration = round(time.perf_counter() - start_time, 4)
            logger.error("AI request failed after %.4fs: %s", duration, str(exc))
            return AIProviderResponse(
                raw_text="",
                parsed_json=None,
                model_used=self._active_model_used,
                processing_time=duration,
                success=False,
                error=str(exc),
            )

    async def review_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate structured code review enriched with static AST findings."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_review_prompt(context)
        return await self._generate_response(prompt)

    async def explain_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate beginner explanation, execution flow, and structural summary."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_explain_prompt(context)
        return await self._generate_response(prompt)

    async def optimize_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate optimized code, performance, and memory suggestions."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_optimize_prompt(context)
        return await self._generate_response(prompt)

    async def fix_code(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Identify bugs and generate corrected code."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_bugfix_prompt(context)
        return await self._generate_response(prompt)

    async def generate_documentation(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate docstrings and documented code."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_documentation_prompt(context)
        return await self._generate_response(prompt)

    async def generate_tests(self, context: AIAnalysisContext) -> AIProviderResponse:
        """Generate pytest test suite."""
        context.source_code = self._sanitize_code(context.source_code)
        prompt = build_unittest_prompt(context)
        return await self._generate_response(prompt)

    async def generate_summary(self, context: AIAnalysisContext) -> str:
        """Generate a concise executive summary."""
        resp = await self.review_code(context)
        if resp.parsed_json and "summary" in resp.parsed_json:
            return resp.parsed_json["summary"]
        return resp.raw_text[:200] if resp.raw_text else "No summary generated."

    async def get_available_models(self) -> List[str]:
        """Return available models."""
        return AVAILABLE_GEMINI_MODELS

    async def health_check(self) -> Dict[str, Any]:
        """Check provider configuration and connectivity."""
        active_key = self.current_api_key
        is_configured = bool(active_key and active_key != "your_gemini_api_key_here")
        return {
            "provider": "gemini",
            "model": self.model,
            "configured": is_configured,
            "status": "ready" if is_configured else "api_key_missing",
            "timeout_seconds": self.timeout,
            "max_retries": self.max_retries,
        }
