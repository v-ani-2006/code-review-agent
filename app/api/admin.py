from typing import Annotated, Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user
from app.db.session import get_db
from app.models.review import Review
from app.models.task import Task
from app.models.upload import Upload
from app.models.user import User
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyUpdate,
)
from app.services.api_key_service import api_key_service
from app.services.cache_service import cache_service
from app.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- System & Subsystem Inspection ---

@router.get(
    "/system",
    status_code=status.HTTP_200_OK,
    summary="Admin System Overview",
    description="Aggregate telemetry overview including hardware diagnostics, subsystem health, and database metrics.",
)
async def get_admin_system_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Get system telemetry overview."""
    return await monitoring_service.get_system_overview(db)


@router.get(
    "/cache",
    status_code=status.HTTP_200_OK,
    summary="Inspect Cache Backend",
    description="Inspect cache operational mode, ping latency, and connection URL.",
)
async def get_admin_cache_status(
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Inspect cache backend."""
    cache_info = await monitoring_service.get_cache_status()
    return cache_info.model_dump()


@router.delete(
    "/cache",
    status_code=status.HTTP_200_OK,
    summary="Flush Cache",
    description="Flush all stored keys from Redis or in-memory cache backend.",
)
async def flush_admin_cache(
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Flush cache storage."""
    success = await cache_service.flush_all()
    return {"success": success, "message": "Cache successfully cleared." if success else "Failed to flush cache."}


@router.get(
    "/redis",
    status_code=status.HTTP_200_OK,
    summary="Inspect Redis Connection",
    description="Direct ping and status verification for the Redis server.",
)
async def get_admin_redis_details(
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Inspect Redis connection."""
    return await monitoring_service.get_cache_status()


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Inspect Performance Metrics",
    description="Retrieve application, AI, upload, and cache performance telemetry summaries.",
)
async def get_admin_metrics(
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Get system performance metrics summary."""
    from app.core.metrics import metrics_collector
    return {
        "application": metrics_collector.get_application_metrics_summary(),
        "cache": metrics_collector.get_cache_metrics_summary(),
        "ai": metrics_collector.get_ai_metrics_summary(),
        "uploads": metrics_collector.get_uploads_metrics_summary(),
    }


# --- Resource Lists for Admin Dashboard ---

@router.get(
    "/tasks",
    status_code=status.HTTP_200_OK,
    summary="List All System Tasks",
    description="Retrieve all background tasks executed across the platform.",
)
async def list_admin_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> Dict[str, Any]:
    """List system background tasks."""
    total = (await db.execute(select(func.count(Task.id)))).scalar() or 0
    stmt = (
        select(Task)
        .order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    res = await db.execute(stmt)
    tasks = res.scalars().all()
    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": [
            {
                "id": str(t.id),
                "user_id": str(t.user_id),
                "task_type": t.task_type,
                "status": t.status,
                "progress_percentage": t.progress_percentage,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ],
    }


@router.get(
    "/uploads",
    status_code=status.HTTP_200_OK,
    summary="List All System Uploads",
    description="Retrieve all file uploads recorded in the system.",
)
async def list_admin_uploads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> Dict[str, Any]:
    """List system uploads."""
    total = (await db.execute(select(func.count(Upload.id)))).scalar() or 0
    stmt = (
        select(Upload)
        .order_by(Upload.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    res = await db.execute(stmt)
    uploads = res.scalars().all()
    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "uploads": [
            {
                "id": str(u.id),
                "user_id": str(u.user_id),
                "original_filename": u.original_filename,
                "file_size": u.file_size,
                "file_hash": u.file_hash,
                "language": u.language,
                "created_at": u.created_at.isoformat(),
            }
            for u in uploads
        ],
    }


@router.get(
    "/reviews",
    status_code=status.HTTP_200_OK,
    summary="List All System Reviews",
    description="Retrieve recent reviews across all platform users.",
)
async def list_admin_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> Dict[str, Any]:
    """List system reviews."""
    total = (await db.execute(select(func.count(Review.id)))).scalar() or 0
    stmt = (
        select(Review)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    res = await db.execute(stmt)
    reviews = res.scalars().all()
    return {
        "success": True,
        "total": total,
        "page": page,
        "page_size": page_size,
        "reviews": [
            {
                "id": str(r.id),
                "user_id": str(r.user_id),
                "filename": r.filename,
                "language": r.language,
                "overall_score": r.overall_score,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    }


# --- API Key Management Endpoints ---

@router.post(
    "/api-keys",
    response_model=APIKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision New API Key",
    description="Create an API key with fine-grained permission scopes. Returns the raw secret key once.",
)
async def create_api_key(
    data: APIKeyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> APIKeyCreateResponse:
    """Provision API key."""
    return await api_key_service.create_api_key(db=db, user=current_admin, data=data)


@router.get(
    "/api-keys",
    response_model=APIKeyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All API Keys",
    description="List all provisioned API keys across the platform.",
)
async def list_api_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> APIKeyListResponse:
    """List API keys."""
    return await api_key_service.list_all_keys(db=db, page=page, page_size=page_size)


@router.patch(
    "/api-keys/{key_id}",
    response_model=APIKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update API Key",
    description="Modify label, active state, or permission scopes of an API key.",
)
async def update_api_key(
    key_id: uuid.UUID,
    data: APIKeyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> APIKeyResponse:
    """Update API key."""
    return await api_key_service.update_key(db=db, key_id=key_id, user=current_admin, data=data)


@router.delete(
    "/api-keys/{key_id}",
    status_code=status.HTTP_200_OK,
    summary="Revoke API Key",
    description="Permanently revoke and delete an API key.",
)
async def revoke_api_key(
    key_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Revoke API key."""
    await api_key_service.delete_key(db=db, key_id=key_id, user=current_admin)
    return {"success": True, "message": f"API key '{key_id}' successfully revoked."}
