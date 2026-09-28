"""FastAPI Router for Hindsight Agent Memory Subsystem.

Exposes RESTful endpoints for:
- POST /api/v1/hindsight/retain   : Store code review observations and conventions
- POST /api/v1/hindsight/recall   : High-speed (< 2ms) semantic recall of past learnings
- POST /api/v1/hindsight/reflect  : Retrospective reasoning & mental model synthesis
- GET  /api/v1/hindsight/memories : Query and list memory units
- DELETE /api/v1/hindsight/memories/{memory_id} : Prune memory item
- GET  /api/v1/hindsight/stats    : Memory bank metrics and telemetry
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.hindsight import (
    HindsightMemoryUnit,
    HindsightRecallRequest,
    HindsightRecallResponse,
    HindsightReflectRequest,
    HindsightReflectResponse,
    HindsightRetainRequest,
    HindsightRetainResponse,
    HindsightStatsResponse,
    MemoryType,
)
from app.services.hindsight_service import hindsight_service

router = APIRouter(prefix="/hindsight", tags=["Hindsight Memory"])


@router.post(
    "/retain",
    response_model=HindsightRetainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Retain Memory Unit",
    description="Ingest a new code convention, anti-pattern, or review observation into Hindsight memory.",
)
async def retain_memory(request: HindsightRetainRequest) -> HindsightRetainResponse:
    """Store knowledge or convention into Hindsight bank."""
    return hindsight_service.retain_memory(request)


@router.post(
    "/recall",
    response_model=HindsightRecallResponse,
    status_code=status.HTTP_200_OK,
    summary="Recall Relevant Memories",
    description="Sub-millisecond hybrid lexical and semantic search to recall relevant conventions for a query or code snippet.",
)
async def recall_memories(request: HindsightRecallRequest) -> HindsightRecallResponse:
    """Search and rank memories relevant to the query or code."""
    return hindsight_service.recall_memories(request)


@router.post(
    "/reflect",
    response_model=HindsightReflectResponse,
    status_code=status.HTTP_200_OK,
    summary="Reflect Across Memory Bank",
    description="Perform retrospective synthesis over historical review memories, deriving mental models and codebase trajectories.",
)
async def reflect_on_history(request: HindsightReflectRequest) -> HindsightReflectResponse:
    """Synthesize mental models, quality trajectories, and guidelines."""
    return hindsight_service.reflect_on_history(request)


@router.get(
    "/memories",
    response_model=List[HindsightMemoryUnit],
    status_code=status.HTTP_200_OK,
    summary="List Stored Memories",
    description="Retrieve stored memory units with optional filtering by type, tag, and pagination.",
)
async def list_memories(
    bank_id: Optional[str] = Query(default=None, description="Memory bank identifier"),
    memory_type: Optional[MemoryType] = Query(default=None, description="Filter by memory classification"),
    tag: Optional[str] = Query(default=None, description="Filter by tag keyword"),
    limit: int = Query(default=50, ge=1, le=200, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
) -> List[HindsightMemoryUnit]:
    """List memory units with filtering."""
    return hindsight_service.list_memories(
        bank_id=bank_id,
        memory_type=memory_type,
        tag=tag,
        limit=limit,
        offset=offset,
    )


@router.delete(
    "/memories/{memory_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Memory Unit",
    description="Remove an obsolete or invalid memory unit from the memory bank.",
)
async def delete_memory(
    memory_id: str,
    bank_id: Optional[str] = Query(default=None, description="Memory bank identifier"),
):
    """Delete a memory unit by ID."""
    deleted = hindsight_service.delete_memory(memory_id=memory_id, bank_id=bank_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory unit '{memory_id}' not found in bank.",
        )
    return {"success": True, "message": f"Memory unit '{memory_id}' deleted successfully."}


@router.get(
    "/stats",
    response_model=HindsightStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Hindsight Bank Telemetry",
    description="Retrieve operational statistics, memory distribution, and recall latency for the Hindsight engine.",
)
async def get_stats(
    bank_id: Optional[str] = Query(default=None, description="Memory bank identifier"),
) -> HindsightStatsResponse:
    """Return memory metrics and telemetry."""
    return hindsight_service.get_stats(bank_id=bank_id)
