from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """Detailed record of an audited system, security, or data modification action."""

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Paginated collection of audit log records."""

    success: bool = True
    total: int
    page: int
    page_size: int
    logs: List[AuditLogResponse] = Field(default_factory=list)


class AuditActionsResponse(BaseModel):
    """List of all registered action identifiers recorded across audit history."""

    success: bool = True
    actions: List[str] = Field(default_factory=list)
