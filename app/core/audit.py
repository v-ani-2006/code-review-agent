from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
import uuid
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.models.audit_log import AuditLog


def extract_client_info(request: Optional[Request]) -> Tuple[Optional[str], Optional[str]]:
    """Extract client IP address and User-Agent from HTTP Request."""
    if not request:
        return None, None

    ip_address = None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    elif request.client and request.client.host:
        ip_address = request.client.host

    user_agent = request.headers.get("User-Agent")
    if user_agent and len(user_agent) > 250:
        user_agent = user_agent[:250] + "..."

    return ip_address, user_agent


async def create_audit_entry(
    db: AsyncSession,
    action: str,
    resource: str,
    user_id: Optional[uuid.UUID] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """Create and persist an audit record in the database."""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            metadata_json=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        logger.info(
            "📝 [AUDIT] %s on %s%s by user %s (status: %s)",
            action,
            resource,
            f" ({resource_id})" if resource_id else "",
            user_id or "anonymous",
            status,
        )
        return log_entry
    except Exception as exc:
        logger.error("Failed to write audit log entry: %s", str(exc))
        await db.rollback()
        raise


async def log_audit_background(
    action: str,
    resource: str,
    user_id: Optional[uuid.UUID] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Background task worker to record audit logs without blocking HTTP response."""
    try:
        async with AsyncSessionLocal() as db:
            await create_audit_entry(
                db=db,
                action=action,
                resource=resource,
                user_id=user_id,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                metadata=metadata,
            )
    except Exception as exc:
        logger.warning("Background audit logging suppressed error: %s", str(exc))
