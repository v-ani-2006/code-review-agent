from datetime import datetime
from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import (
    AuditActionsResponse,
    AuditLogListResponse,
    AuditLogResponse,
)
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and Filter Audit Logs",
    description="Retrieve paginated security, lifecycle, and operational audit trail logs with dynamic filters.",
)
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    resource: Optional[str] = Query(None, description="Filter by resource type"),
    log_status: Optional[str] = Query(None, alias="status", description="Filter by outcome status (success, failure, denied)"),
    start_date: Optional[datetime] = Query(None, description="ISO start timestamp filter"),
    end_date: Optional[datetime] = Query(None, description="ISO end timestamp filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
) -> AuditLogListResponse:
    """Query audit logs."""
    return await audit_service.list_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource=resource,
        status_filter=log_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/actions",
    response_model=AuditActionsResponse,
    status_code=status.HTTP_200_OK,
    summary="List Distinct Audit Actions",
    description="Fetch list of all unique action identifiers registered across the audit log history.",
)
async def get_distinct_audit_actions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> AuditActionsResponse:
    """Get unique action types."""
    return await audit_service.get_distinct_actions(db)


@router.get(
    "/export",
    summary="Export Audit Trail Data",
    description="Export filtered audit logs formatted as JSON or CSV file.",
)
async def export_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    export_format: str = Query("json", alias="format", description="Export format: 'json' or 'csv'"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource: Optional[str] = Query(None, description="Filter by resource"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
) -> Response:
    """Export audit logs as JSON or CSV."""
    exported_data = await audit_service.export_logs(
        db=db,
        export_format=export_format,
        user_id=user_id,
        action=action,
        resource=resource,
    )
    if export_format.lower() == "csv":
        return Response(
            content=exported_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_export.csv"},
        )
    return Response(
        content=exported_data,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=audit_export.json"},
    )


@router.get(
    "/user/{user_id}",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Audit Trail",
    description="Retrieve all operational actions performed by a specific user.",
)
async def get_user_audit_logs(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> AuditLogListResponse:
    """Get audit logs for a single user."""
    return await audit_service.get_user_logs(db=db, user_id=user_id, page=page, page_size=page_size)


@router.get(
    "/{log_id}",
    response_model=AuditLogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Audit Log Entry",
    description="Fetch a single audit log entry by its UUID.",
)
async def get_audit_log_entry(
    log_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_admin_user)],
) -> AuditLogResponse:
    """Get single audit log entry."""
    return await audit_service.get_log_by_id(db=db, log_id=log_id)
