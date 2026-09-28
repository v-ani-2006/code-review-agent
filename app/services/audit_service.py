import csv
from datetime import datetime
import io
import json
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import audit_repository
from app.schemas.audit import (
    AuditActionsResponse,
    AuditLogListResponse,
    AuditLogResponse,
)


class AuditService:
    """Service providing search, inspection, analytics, and data export for security audit logs."""

    async def list_logs(
        self,
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        status_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> AuditLogListResponse:
        """Query paginated audit logs based on search criteria."""
        items, total = await audit_repository.list_audit_logs(
            db=db,
            user_id=user_id,
            action=action,
            resource=resource,
            status=status_filter,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return AuditLogListResponse(
            total=total,
            page=page,
            page_size=page_size,
            logs=[AuditLogResponse.model_validate(log) for log in items],
        )

    async def get_log_by_id(self, db: AsyncSession, log_id: uuid.UUID) -> AuditLogResponse:
        """Fetch a single audit log entry by ID."""
        item = await audit_repository.get_by_id(db, log_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit log entry '{log_id}' not found.",
            )
        return AuditLogResponse.model_validate(item)

    async def get_user_logs(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> AuditLogListResponse:
        """Retrieve audit history for a single user."""
        items, total = await audit_repository.get_by_user(db, user_id=user_id, page=page, page_size=page_size)
        return AuditLogListResponse(
            total=total,
            page=page,
            page_size=page_size,
            logs=[AuditLogResponse.model_validate(log) for log in items],
        )

    async def get_distinct_actions(self, db: AsyncSession) -> AuditActionsResponse:
        """Fetch all unique recorded action identifiers."""
        actions = await audit_repository.get_distinct_actions(db)
        return AuditActionsResponse(actions=actions)

    async def export_logs(
        self,
        db: AsyncSession,
        export_format: str = "json",
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> str:
        """Export audit logs formatted as JSON or CSV."""
        items, _ = await audit_repository.list_audit_logs(
            db=db,
            user_id=user_id,
            action=action,
            resource=resource,
            page=1,
            page_size=1000,
        )

        if export_format.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "timestamp", "user_id", "action", "resource", "resource_id", "status", "ip_address"])
            for log in items:
                writer.writerow([
                    str(log.id),
                    log.timestamp.isoformat(),
                    str(log.user_id) if log.user_id else "",
                    log.action,
                    log.resource,
                    log.resource_id or "",
                    log.status,
                    log.ip_address or "",
                ])
            return output.getvalue()

        # Default JSON export
        log_dicts = [
            {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.metadata_json,
            }
            for log in items
        ]
        return json.dumps({"audit_logs": log_dicts}, indent=2)


audit_service = AuditService()
