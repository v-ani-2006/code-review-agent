"""Hindsight Service Orchestrator.

Bridges the code review pipeline with Hindsight Agent Memory.
Provides automated pre-review recall and post-review retention loops,
ensuring the agent learns from historical reviews and project conventions.
"""
import time
from typing import Any, Dict, List, Optional

from app.ai.hindsight import hindsight_engine
from app.core.config import settings
from app.core.logging import logger
from app.schemas.hindsight import (
    HindsightMemoryUnit,
    HindsightRecallRequest,
    HindsightRecallResponse,
    HindsightRecallResult,
    HindsightReflectRequest,
    HindsightReflectResponse,
    HindsightRetainRequest,
    HindsightRetainResponse,
    HindsightStatsResponse,
    MemoryType,
)
from app.schemas.review import ReviewReport


class HindsightService:
    """Service layer managing Hindsight memory operations and review integration."""

    def __init__(self):
        self._engine = hindsight_engine
        self._client = None
        self._client_attempted = False

    @property
    def client(self):
        """Lazy access to external Hindsight client if remote server is explicitly configured."""
        if not self._client_attempted:
            self._client_attempted = True
            if settings.HINDSIGHT_BASE_URL and settings.HINDSIGHT_BASE_URL != "http://localhost:8888":
                try:
                    from hindsight_client import Hindsight
                    self._client = Hindsight(
                        base_url=settings.HINDSIGHT_BASE_URL,
                        timeout=1.0,
                        max_attempts=1,
                    )
                except Exception as e:
                    logger.debug("Hindsight remote client not initialized: %s", e)
                    self._client = None
            else:
                self._client = None
        return self._client

    # ---------------- 1. RETAIN ----------------
    def retain_memory(self, request: HindsightRetainRequest) -> HindsightRetainResponse:
        """Retain a memory unit into Hindsight bank."""
        start = time.perf_counter()
        bank_id = request.bank_id or settings.HINDSIGHT_BANK_ID

        # Primary: retain in fast embedded engine
        unit = self._engine.retain(
            bank_id=bank_id,
            content=request.content,
            memory_type=request.memory_type,
            tags=request.tags,
            filename_pattern=request.filename_pattern,
            language=request.language,
            metadata=request.metadata,
            source="api",
        )

        # Secondary: if external client is configured, best-effort non-blocking sync
        if self.client:
            try:
                ret = self.client.retain(
                    bank_id=bank_id,
                    content=request.content,
                    tags=request.tags,
                )
                if hasattr(ret, "__await__"):
                    import asyncio
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(ret)
                    except Exception:
                        pass
            except Exception as exc:
                logger.debug("Hindsight client remote sync skipped: %s", exc)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return HindsightRetainResponse(
            success=True,
            message="Memory unit retained into Hindsight bank successfully.",
            memory=unit,
            execution_time_ms=round(elapsed_ms, 2),
        )

    # ---------------- 2. RECALL ----------------
    def recall_memories(self, request: HindsightRecallRequest) -> HindsightRecallResponse:
        """Recall relevant memories for query or code snippet."""
        start = time.perf_counter()
        bank_id = request.bank_id or settings.HINDSIGHT_BANK_ID

        results = self._engine.recall(
            bank_id=bank_id,
            query=request.query,
            top_k=request.top_k,
            min_confidence=request.min_confidence,
            memory_types=request.memory_types,
            tags=request.tags,
            language=request.language,
            filename=request.filename,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return HindsightRecallResponse(
            success=True,
            bank_id=bank_id,
            query=request.query[:120] + ("..." if len(request.query) > 120 else ""),
            results=results,
            count=len(results),
            execution_time_ms=round(elapsed_ms, 2),
            engine="Hindsight Embedded Fast Semantic v1.0",
        )

    # ---------------- 3. REFLECT ----------------
    def reflect_on_history(self, request: HindsightReflectRequest) -> HindsightReflectResponse:
        """Perform retrospective reflection across stored memories."""
        bank_id = request.bank_id or settings.HINDSIGHT_BANK_ID
        reflection_dict = self._engine.reflect(
            bank_id=bank_id,
            query=request.query,
            focus=request.focus,
        )

        return HindsightReflectResponse(
            success=True,
            bank_id=bank_id,
            query=request.query or "General reflection",
            synthesis=reflection_dict["synthesis"],
            mental_models=reflection_dict["mental_models"],
            quality_trajectory=reflection_dict["quality_trajectory"],
            actionable_guidelines=reflection_dict["actionable_guidelines"],
            memories_analyzed=reflection_dict["memories_analyzed"],
            execution_time_ms=reflection_dict["execution_time_ms"],
        )

    # ---------------- 4. CODE REVIEW INTEGRATION ----------------
    def auto_retain_from_review(
        self,
        code: str,
        filename: str,
        language: str,
        review_data: Any,
        static_report: ReviewReport,
        bank_id: Optional[str] = None,
    ) -> List[HindsightMemoryUnit]:
        """Auto-retain lessons, security catches, and anti-patterns from a completed code review."""
        if not settings.HINDSIGHT_AUTO_RETAIN:
            return []

        retained: List[HindsightMemoryUnit] = []
        target_bank = bank_id or settings.HINDSIGHT_BANK_ID

        # 1. Retain critical or high security issues as historical security rules
        for finding in static_report.security_findings:
            if finding.severity in ("HIGH", "CRITICAL"):
                content = (
                    f"In file '{filename}' ({language}): detected security vulnerability '{finding.title}'. "
                    f"Description: {finding.description}. Remediation: {finding.recommendation or 'Sanitize inputs'}."
                )
                unit = self._engine.retain(
                    bank_id=target_bank,
                    content=content,
                    memory_type=MemoryType.SECURITY_RULE,
                    tags=["security", finding.cwe_id.lower() if finding.cwe_id else "vuln", language.lower()],
                    filename_pattern=filename,
                    language=language,
                    source="auto_retain",
                    metadata={"severity": finding.severity, "line": finding.line_number},
                )
                retained.append(unit)

        # 2. Retain high complexity anti-patterns
        if static_report.complexity.cyclomatic_complexity > 12:
            content = (
                f"File '{filename}' exhibited elevated Cyclomatic Complexity ({static_report.complexity.cyclomatic_complexity}, "
                f"Rank {static_report.complexity.rank}). Large functions require decomposition to prevent maintenance debt."
            )
            unit = self._engine.retain(
                bank_id=target_bank,
                content=content,
                memory_type=MemoryType.ANTI_PATTERN,
                tags=["complexity", "radon", "refactoring", language.lower()],
                filename_pattern=filename,
                language=language,
                source="auto_retain",
            )
            retained.append(unit)

        # 3. Retain key optimization or refactoring suggestion from AI review
        suggestions = getattr(review_data, "optimization_suggestions", []) or []
        if suggestions and isinstance(suggestions, list):
            top_suggestion = str(suggestions[0])
            if len(top_suggestion) > 20:
                content = f"Historical lesson for '{filename}': {top_suggestion}"
                unit = self._engine.retain(
                    bank_id=target_bank,
                    content=content,
                    memory_type=MemoryType.REFACTOR_DECISION,
                    tags=["optimization", "review", language.lower()],
                    filename_pattern=filename,
                    language=language,
                    source="auto_retain",
                )
                retained.append(unit)

        return retained

    def format_hindsight_context(self, recall_results: List[HindsightRecallResult]) -> str:
        """Format recalled memories into markdown bullet points for LLM prompt context."""
        if not recall_results:
            return ""

        lines = [
            "### Hindsight Agent Memory (Historical Lessons & Codebase Conventions):",
            "The following team conventions, security precedents, and lessons were recalled from past reviews:",
        ]
        for res in recall_results:
            m = res.memory
            tag_str = f" [{', '.join(m.tags)}]" if m.tags else ""
            lines.append(f"- **[{m.memory_type.value.upper()}]** {m.content}{tag_str} *(Relevance: {int(res.relevance_score * 100)}%)*")

        lines.append(
            "\n**Instruction:** Actively evaluate whether the submitted code adheres to or violates "
            "these recalled historical conventions, and reference them in your architectural critique if relevant."
        )
        return "\n".join(lines)

    # ---------------- 5. STATS & MANAGEMENT ----------------
    def get_stats(self, bank_id: Optional[str] = None) -> HindsightStatsResponse:
        """Return memory bank telemetry and health metrics."""
        stats = self._engine.get_stats(bank_id=bank_id)
        stats["client_connected"] = bool(self.client is not None)
        return HindsightStatsResponse(**stats)

    def list_memories(
        self,
        bank_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HindsightMemoryUnit]:
        """List stored memories with filtering."""
        return self._engine.list_memories(
            bank_id=bank_id,
            memory_type=memory_type,
            tag=tag,
            limit=limit,
            offset=offset,
        )

    def delete_memory(self, memory_id: str, bank_id: Optional[str] = None) -> bool:
        """Remove a memory by ID."""
        return self._engine.delete_memory(memory_id=memory_id, bank_id=bank_id)


# Global singleton instance
hindsight_service = HindsightService()
