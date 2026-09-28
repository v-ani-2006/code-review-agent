"""Pydantic schemas and data transfer models for Hindsight Agent Memory.

Provides schemas for:
- Retain: ingesting observations, conventions, and review learnings.
- Recall: high-speed semantic retrieval of relevant memories.
- Reflect: agentic synthesis of mental models and quality trends over memory banks.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Classification of Hindsight memory units."""
    CONVENTION = "convention"
    ANTI_PATTERN = "anti_pattern"
    OBSERVATION = "observation"
    SECURITY_RULE = "security_rule"
    USER_FEEDBACK = "user_feedback"
    REFACTOR_DECISION = "refactor_decision"


class HindsightMemoryUnit(BaseModel):
    """A durable atomic unit of memory stored within a Hindsight bank."""
    id: str = Field(description="Unique identifier for this memory unit")
    bank_id: str = Field(description="Memory bank identifier")
    memory_type: MemoryType = Field(default=MemoryType.CONVENTION, description="Category of memory")
    content: str = Field(description="Textual knowledge or convention retained")
    confidence: float = Field(default=1.0, description="Base confidence score (0.0 - 1.0)")
    tags: List[str] = Field(default_factory=list, description="Categorical or semantic tags")
    filename_pattern: Optional[str] = Field(default=None, description="Optional filename glob or pattern match")
    language: Optional[str] = Field(default=None, description="Programming language scope")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp")
    access_count: int = Field(default=0, description="Frequency of recall accesses")
    source: str = Field(default="system", description="Origin: seed, auto_retain, user, api")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary supplemental metadata")


class HindsightRetainRequest(BaseModel):
    """Payload to retain a new memory or convention."""
    bank_id: Optional[str] = Field(default=None, description="Target bank id (defaults to configured bank)")
    content: str = Field(..., min_length=3, description="Memory content to retain")
    memory_type: MemoryType = Field(default=MemoryType.CONVENTION, description="Type of memory")
    tags: List[str] = Field(default_factory=list, description="Descriptive tags")
    filename_pattern: Optional[str] = Field(default=None, description="Optional filename filter pattern")
    language: Optional[str] = Field(default=None, description="Language constraint (e.g. python, typescript)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom contextual metadata")


class HindsightRetainResponse(BaseModel):
    """Result of retaining a memory unit."""
    success: bool
    message: str
    memory: HindsightMemoryUnit
    execution_time_ms: float


class HindsightRecallRequest(BaseModel):
    """Query parameters to recall relevant memories."""
    bank_id: Optional[str] = Field(default=None, description="Target bank id")
    query: str = Field(..., min_length=1, description="Search query or source code snippet")
    top_k: int = Field(default=5, ge=1, le=50, description="Max memories to return")
    min_confidence: float = Field(default=0.2, ge=0.0, le=1.0, description="Minimum relevance score threshold")
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Filter by specific memory types")
    tags: Optional[List[str]] = Field(default=None, description="Filter by required tags")
    language: Optional[str] = Field(default=None, description="Filter by language match")
    filename: Optional[str] = Field(default=None, description="Filter or rank by target filename")


class HindsightRecallResult(BaseModel):
    """A scored memory item returned from recall."""
    memory: HindsightMemoryUnit
    relevance_score: float = Field(description="Computed semantic & keyword relevance score (0.0 - 1.0)")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that triggered the match")


class HindsightRecallResponse(BaseModel):
    """Recall results package."""
    success: bool
    bank_id: str
    query: str
    results: List[HindsightRecallResult]
    count: int
    execution_time_ms: float
    engine: str


class HindsightReflectRequest(BaseModel):
    """Request for agentic reflection across the memory bank."""
    bank_id: Optional[str] = Field(default=None, description="Target bank id")
    query: Optional[str] = Field(
        default="Synthesize codebase anti-patterns, recurrent security pitfalls, and team conventions.",
        description="Reflection guidance prompt",
    )
    focus: Optional[str] = Field(default=None, description="Optional focus area: security, performance, style, architecture")


class HindsightMentalModel(BaseModel):
    """A synthesized conceptual rule derived from multiple historical memories."""
    title: str
    summary: str
    evidence_count: int
    severity: str
    actionable_directive: str


class HindsightReflectResponse(BaseModel):
    """Agentic retrospective reflection synthesis."""
    success: bool
    bank_id: str
    query: str
    synthesis: str
    mental_models: List[HindsightMentalModel]
    quality_trajectory: str
    actionable_guidelines: List[str]
    memories_analyzed: int
    execution_time_ms: float


class HindsightStatsResponse(BaseModel):
    """Telemetry and operational metrics for Hindsight memory banks."""
    bank_id: str
    total_memories: int
    by_type: Dict[str, int]
    by_language: Dict[str, int]
    active_engine: str
    client_connected: bool
    avg_recall_latency_ms: float
