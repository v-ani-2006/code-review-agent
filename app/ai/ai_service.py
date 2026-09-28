from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.ai.analyzer import analyze_code
from app.ai.constants import SUPPORTED_LANGUAGES
from app.ai.formatter import format_review_summary_markdown
from app.ai.models import AIAnalysisContext, AIProviderResponse
from app.ai.parser import (
    extract_first_code_block,
    extract_json_fragment,
    normalize_whitespace,
    safe_parse_json,
)
from app.ai.providers.provider_factory import get_ai_provider
from app.core.config import settings
from app.core.logging import logger
from app.schemas.ai_review import (
    AIBugFixData,
    AIBugFixRequest,
    AIBugFixResponse,
    AIDocumentationData,
    AIDocumentationRequest,
    AIDocumentationResponse,
    AIExplainData,
    AIExplainRequest,
    AIExplainResponse,
    AIModelListResponse,
    AIOptimizeData,
    AIOptimizeRequest,
    AIOptimizeResponse,
    AIReviewData,
    AIReviewRequest,
    AIReviewResponse,
    AIStatusResponse,
    AITestData,
    AITestRequest,
    AITestResponse,
)
from app.schemas.hindsight import HindsightRecallRequest
from app.schemas.review import ReviewReport
from app.ai.hindsight_service import hindsight_service


class AIService:
    """Core AI orchestration service.

    Validates incoming payloads, executes Phase 5 static AST/Radon/Bandit analysis,
    queries Hindsight Agent Memory for historical conventions, merges findings into a rich AI context,
    and delegates to AI providers for reasoning.
    """

    def _validate_request(self, code: str, language: str) -> None:
        """Validate input code and language."""
        if not code or not code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source code cannot be empty.",
            )
        if language.lower().strip() not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language '{language}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}.",
            )

    def _build_context(
        self,
        code: str,
        filename: str,
        language: str,
        report: ReviewReport,
        recalled_memories: Optional[List[Any]] = None,
    ) -> AIAnalysisContext:
        """Create structured AIAnalysisContext from static analyzer report and Hindsight memory."""
        mem_dicts = []
        prompt_ctx = ""
        if recalled_memories:
            mem_dicts = [
                {
                    "id": r.memory.id,
                    "type": r.memory.memory_type.value,
                    "content": r.memory.content,
                    "confidence": r.memory.confidence,
                    "relevance_score": r.relevance_score,
                    "tags": r.memory.tags,
                }
                for r in recalled_memories
            ]
            prompt_ctx = hindsight_service.format_hindsight_context(recalled_memories)

        return AIAnalysisContext(
            language=language.lower().strip(),
            filename=(filename or "main.py").strip(),
            source_code=code,
            summary=report.summary,
            overall_score=report.scores.overall,
            readability_score=report.scores.readability,
            maintainability_score=report.scores.maintainability,
            security_score=report.scores.security,
            complexity_score=report.scores.complexity,
            documentation_score=report.scores.documentation,
            cyclomatic_complexity=report.complexity.cyclomatic_complexity,
            complexity_rank=report.complexity.rank,
            issues=[issue.model_dump() for issue in report.issues],
            security_findings=[sec.model_dump() for sec in report.security_findings],
            style_findings=report.style,
            metrics=report.metrics.model_dump(),
            metadata=report.metadata,
            hindsight_memories=mem_dicts,
            hindsight_prompt_context=prompt_ctx,
        )

    # --- 1. AI REVIEW WITH HINDSIGHT MEMORY ---
    async def review_code(self, request: AIReviewRequest) -> AIReviewResponse:
        """Execute Phase 5 static AST analysis and enrich with Gemini AI reasoning & Hindsight memory."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        # Step 1: Static AST / Complexity / Security analysis
        static_report = analyze_code(
            code=request.code,
            filename=request.filename,
            language=request.language,
        )

        # Step 2: Query Hindsight Agent Memory (Recall past conventions & anti-patterns)
        recalled_memories = []
        if settings.HINDSIGHT_ENABLED and settings.HINDSIGHT_AUTO_RECALL:
            try:
                recall_resp = hindsight_service.recall_memories(
                    HindsightRecallRequest(
                        query=request.code,
                        language=request.language,
                        filename=request.filename,
                        top_k=settings.HINDSIGHT_TOP_K,
                        min_confidence=settings.HINDSIGHT_MIN_CONFIDENCE,
                    )
                )
                recalled_memories = recall_resp.results
            except Exception as hs_exc:
                logger.warning("Hindsight memory recall encountered non-fatal error: %s", hs_exc)

        hindsight_payload = [
            {
                "id": r.memory.id,
                "type": r.memory.memory_type.value,
                "content": r.memory.content,
                "confidence": r.memory.confidence,
                "relevance_score": r.relevance_score,
                "tags": r.memory.tags,
                "matched_keywords": r.matched_keywords,
            }
            for r in recalled_memories
        ]

        # Step 3: Assemble context for AI reasoning
        context = self._build_context(
            request.code,
            request.filename or "main.py",
            request.language,
            static_report,
            recalled_memories,
        )
        provider = get_ai_provider(model=request.model)

        # Step 4: Call AI Provider (exceptions are caught and surfaced as fallback)
        try:
            provider_resp = await provider.review_code(context)
        except Exception as provider_exc:
            logger.warning("AI provider raised exception: %s. Using static-only fallback.", str(provider_exc))
            from app.ai.providers.base import AIProviderResponse
            provider_resp = AIProviderResponse(
                raw_text="",
                parsed_json=None,
                model_used=getattr(provider, "model", "unknown"),
                processing_time=0.0,
                success=False,
                error=str(provider_exc),
            )
        duration = round(time.perf_counter() - start_time, 4)

        if not provider_resp.success or not provider_resp.parsed_json:
            logger.warning("AI provider review did not return parsed JSON (%s). Generating fallback review.", provider_resp.error)
            critical_list = [f"[{i.severity}] {i.title}: {i.description}" for i in static_report.issues if i.severity in ("HIGH", "CRITICAL")]
            review_data = AIReviewData(
                summary=f"Automated review based on Phase 5 static analysis with Hindsight memory (AI layer note: {provider_resp.error or 'raw output returned'}).",
                overall_assessment=(
                    f"Static quality score: {static_report.scores.overall}/100. "
                    f"Readability: {static_report.scores.readability}/100, Security: {static_report.scores.security}/100. "
                    f"Hindsight recalled {len(recalled_memories)} historical conventions."
                ),
                strengths=["Code parsed successfully", f"Complexity rank: {static_report.complexity.rank}"],
                critical_issues=critical_list,
                security_analysis=f"Found {len(static_report.security_findings)} static security findings.",
                complexity_analysis=f"Average cyclomatic complexity: {static_report.complexity.cyclomatic_complexity}.",
                readability_analysis=f"Readability score: {static_report.scores.readability}/100.",
                maintainability_analysis=f"Maintainability score: {static_report.scores.maintainability}/100.",
                optimization_suggestions=["Review long functions and loops identified in AST analysis."],
                refactoring_suggestions=["Decompose high-complexity functions."],
                best_practices=["Add comprehensive type annotations and docstrings."],
                next_steps=["Address critical security issues first.", "Refactor high complexity blocks."],
                hindsight_context=hindsight_payload,
                metadata={"ai_success": False, "ai_error": provider_resp.error, "hindsight_count": len(recalled_memories)},
            )

            # Auto-retain observations for future reviews
            if settings.HINDSIGHT_ENABLED and settings.HINDSIGHT_AUTO_RETAIN:
                try:
                    hindsight_service.auto_retain_from_review(
                        code=request.code,
                        filename=request.filename or "main.py",
                        language=request.language,
                        review_data=review_data,
                        static_report=static_report,
                    )
                except Exception as auto_exc:
                    logger.debug("Hindsight auto-retain skipped: %s", auto_exc)

            return AIReviewResponse(
                success=True,
                message="Code review generated with Phase 5 static findings and Hindsight memory.",
                processing_time=duration,
                model_used=provider_resp.model_used,
                review=review_data,
                static_report=static_report,
                hindsight_context=hindsight_payload,
            )

        data = provider_resp.parsed_json
        review_data = AIReviewData(
            summary=data.get("summary", static_report.summary),
            overall_assessment=data.get("overall_assessment"),
            strengths=data.get("strengths", []),
            critical_issues=data.get("critical_issues", []),
            security_analysis=data.get("security_analysis"),
            complexity_analysis=data.get("complexity_analysis"),
            readability_analysis=data.get("readability_analysis"),
            maintainability_analysis=data.get("maintainability_analysis"),
            optimization_suggestions=data.get("optimization_suggestions", []),
            refactoring_suggestions=data.get("refactoring_suggestions", []),
            best_practices=data.get("best_practices", []),
            next_steps=data.get("next_steps", []),
            hindsight_context=hindsight_payload,
            metadata={"ai_success": True, "static_overall_score": static_report.scores.overall, "hindsight_count": len(recalled_memories)},
        )

        # Auto-retain observations for future reviews
        if settings.HINDSIGHT_ENABLED and settings.HINDSIGHT_AUTO_RETAIN:
            try:
                hindsight_service.auto_retain_from_review(
                    code=request.code,
                    filename=request.filename or "main.py",
                    language=request.language,
                    review_data=review_data,
                    static_report=static_report,
                )
            except Exception as auto_exc:
                logger.debug("Hindsight auto-retain skipped: %s", auto_exc)

        return AIReviewResponse(
            success=True,
            message="Comprehensive AI and static code review generated with Hindsight memory.",
            processing_time=duration,
            model_used=provider_resp.model_used,
            review=review_data,
            static_report=static_report,
            hindsight_context=hindsight_payload,
        )

    # --- 2. AI EXPLAIN ---
    async def explain_code(self, request: AIExplainRequest) -> AIExplainResponse:
        """Generate beginner explanation, execution flow, and structural summary."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        static_report = analyze_code(request.code, request.filename, request.language)
        context = self._build_context(request.code, request.filename or "main.py", request.language, static_report)
        provider = get_ai_provider(model=request.model)

        provider_resp = await provider.explain_code(context)
        duration = round(time.perf_counter() - start_time, 4)

        if not provider_resp.success or not provider_resp.parsed_json:
            parsed = extract_json_fragment(provider_resp.raw_text) or {}
            explain_data = AIExplainData(
                beginner_explanation=parsed.get("beginner_explanation", provider_resp.raw_text or "No explanation generated."),
                line_by_line_summary=parsed.get("line_by_line_summary", []),
                execution_flow=parsed.get("execution_flow", []),
                function_explanations=parsed.get("function_explanations", []),
                class_explanations=parsed.get("class_explanations", []),
                key_concepts=parsed.get("key_concepts", []),
            )
        else:
            data = provider_resp.parsed_json
            explain_data = AIExplainData(
                beginner_explanation=data.get("beginner_explanation", "Code walkthrough"),
                line_by_line_summary=data.get("line_by_line_summary", []),
                execution_flow=data.get("execution_flow", []),
                function_explanations=data.get("function_explanations", []),
                class_explanations=data.get("class_explanations", []),
                key_concepts=data.get("key_concepts", []),
            )

        return AIExplainResponse(
            success=provider_resp.success,
            message="Code explanation generated successfully." if provider_resp.success else (provider_resp.error or "Explanation failed"),
            processing_time=duration,
            model_used=provider_resp.model_used,
            data=explain_data,
        )

    # --- 3. AI OPTIMIZE ---
    async def optimize_code(self, request: AIOptimizeRequest) -> AIOptimizeResponse:
        """Generate performance, memory, and idiomatic optimizations."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        static_report = analyze_code(request.code, request.filename, request.language)
        context = self._build_context(request.code, request.filename or "main.py", request.language, static_report)
        provider = get_ai_provider(model=request.model)

        provider_resp = await provider.optimize_code(context)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        optimized_code = data.get("optimized_code") or extract_first_code_block(provider_resp.raw_text) or request.code

        optimize_data = AIOptimizeData(
            optimized_code=optimized_code,
            performance_improvements=data.get("performance_improvements", []),
            memory_improvements=data.get("memory_improvements", []),
            pythonic_improvements=data.get("pythonic_improvements", []),
            time_complexity_before=data.get("time_complexity_before"),
            time_complexity_after=data.get("time_complexity_after"),
            space_complexity_before=data.get("space_complexity_before"),
            space_complexity_after=data.get("space_complexity_after"),
        )

        return AIOptimizeResponse(
            success=provider_resp.success,
            message="Code optimization generated successfully." if provider_resp.success else (provider_resp.error or "Optimization failed"),
            processing_time=duration,
            model_used=provider_resp.model_used,
            data=optimize_data,
        )

    # --- 4. AI BUG FIX ---
    async def fix_code(self, request: AIBugFixRequest) -> AIBugFixResponse:
        """Diagnose bugs and generate corrected source code."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        static_report = analyze_code(request.code, request.filename, request.language)
        context = self._build_context(request.code, request.filename or "main.py", request.language, static_report)
        provider = get_ai_provider(model=request.model)

        provider_resp = await provider.fix_code(context)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        corrected_code = data.get("corrected_code") or extract_first_code_block(provider_resp.raw_text) or request.code

        bugfix_data = AIBugFixData(
            corrected_code=corrected_code,
            identified_bugs=data.get("identified_bugs", []),
            changed_sections=data.get("changed_sections", []),
            reasons_for_changes=data.get("reasons_for_changes", []),
            verification_steps=data.get("verification_steps", []),
        )

        return AIBugFixResponse(
            success=provider_resp.success,
            message="Bug fixes and corrected code generated successfully." if provider_resp.success else (provider_resp.error or "Bug fix failed"),
            processing_time=duration,
            model_used=provider_resp.model_used,
            data=bugfix_data,
        )

    # --- 5. AI DOCUMENTATION ---
    async def generate_documentation(self, request: AIDocumentationRequest) -> AIDocumentationResponse:
        """Generate docstrings and documented code."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        static_report = analyze_code(request.code, request.filename, request.language)
        context = self._build_context(request.code, request.filename or "main.py", request.language, static_report)
        provider = get_ai_provider(model=request.model)

        provider_resp = await provider.generate_documentation(context)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        documented_code = data.get("documented_code") or extract_first_code_block(provider_resp.raw_text) or request.code

        doc_data = AIDocumentationData(
            documented_code=documented_code,
            module_docstring=data.get("module_docstring"),
            class_docstrings=data.get("class_docstrings", []),
            function_docstrings=data.get("function_docstrings", []),
            parameter_descriptions=data.get("parameter_descriptions", []),
            usage_examples=data.get("usage_examples", []),
        )

        return AIDocumentationResponse(
            success=provider_resp.success,
            message="Code documentation generated successfully." if provider_resp.success else (provider_resp.error or "Documentation failed"),
            processing_time=duration,
            model_used=provider_resp.model_used,
            data=doc_data,
        )

    # --- 6. AI UNIT TESTS ---
    async def generate_tests(self, request: AITestRequest) -> AITestResponse:
        """Generate complete pytest test suite."""
        start_time = time.perf_counter()
        self._validate_request(request.code, request.language)

        static_report = analyze_code(request.code, request.filename, request.language)
        context = self._build_context(request.code, request.filename or "main.py", request.language, static_report)
        provider = get_ai_provider(model=request.model)

        provider_resp = await provider.generate_tests(context)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        test_code = data.get("test_code") or extract_first_code_block(provider_resp.raw_text) or "# No tests generated"

        test_data = AITestData(
            test_code=test_code,
            test_framework=data.get("test_framework", "pytest"),
            fixtures=data.get("fixtures", []),
            covered_edge_cases=data.get("covered_edge_cases", []),
            parameterized_cases=data.get("parameterized_cases", []),
            execution_command=data.get("execution_command", "pytest -v"),
        )

        return AITestResponse(
            success=provider_resp.success,
            message="Pytest test suite generated successfully." if provider_resp.success else (provider_resp.error or "Test generation failed"),
            processing_time=duration,
            model_used=provider_resp.model_used,
            data=test_data,
        )

    # --- 7. MODELS & STATUS ---
    async def get_models(self) -> AIModelListResponse:
        """Return supported AI models."""
        provider = get_ai_provider()
        models = await provider.get_available_models()
        return AIModelListResponse(
            success=True,
            provider="gemini",
            default_model=settings.GEMINI_MODEL or "gemini-2.5-flash",
            available_models=models,
        )

    async def get_status(self) -> AIStatusResponse:
        """Return AI provider connectivity and health status."""
        provider = get_ai_provider()
        health = await provider.health_check()
        return AIStatusResponse(
            success=True,
            provider="gemini",
            configured=health.get("configured", False),
            status=health.get("status", "unknown"),
            model=health.get("model", settings.GEMINI_MODEL),
            timeout_seconds=health.get("timeout_seconds", settings.AI_TIMEOUT_SECONDS),
            max_retries=health.get("max_retries", settings.AI_MAX_RETRIES),
        )


# Singleton AI service
ai_service = AIService()
