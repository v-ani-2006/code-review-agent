from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import and_, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository handling search, filtering, and export for immutable AuditLog entries."""

    def __init__(self):
        super().__init__(AuditLog)

    async def list_audit_logs(
        self,
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """Query audit logs with dynamic multi-criteria filtering and pagination."""
        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action.ilike(f"%{action}%"))
        if resource:
            filters.append(AuditLog.resource == resource)
        if status:
            filters.append(AuditLog.status == status)
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)

        where_clause = and_(*filters) if filters else True

        # Total count query
        count_stmt = select(func.count(AuditLog.id)).where(where_clause)
        total = (await db.execute(count_stmt)).scalar() or 0

        # Items query
        stmt = (
            select(AuditLog)
            .where(where_clause)
            .order_by(AuditLog.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_distinct_actions(self, db: AsyncSession) -> List[str]:
        """Fetch all unique audit action names recorded in the system."""
        stmt = select(distinct(AuditLog.action)).order_by(AuditLog.action)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """Fetch audit trail for a specific user ID."""
        return await self.list_audit_logs(db, user_id=user_id, page=page, page_size=page_size)


audit_repository = AuditRepository()
