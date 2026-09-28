from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class WebhookCreate(BaseModel):
    """Payload to register a new webhook subscriber."""

    url: str = Field(..., description="Target HTTP POST URL to receive payloads", min_length=10, max_length=500)
    secret: Optional[str] = Field(None, description="HMAC-SHA256 signature secret (auto-generated if omitted)", max_length=255)
    event_type: str = Field("*", description="Subscribed event type (e.g., 'review.completed', 'upload.completed', or '*' for all)")


class WebhookUpdate(BaseModel):
    """Payload to update an existing webhook registration."""

    url: Optional[str] = Field(None, min_length=10, max_length=500)
    event_type: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    """Detailed Webhook subscriber record."""

    id: uuid.UUID
    user_id: uuid.UUID
    url: str
    event_type: str
    is_active: bool
    last_success_at: Optional[datetime] = None
    failure_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookListResponse(BaseModel):
    """Collection of user-configured webhooks."""

    success: bool = True
    total: int
    webhooks: List[WebhookResponse] = Field(default_factory=list)


class WebhookTestResponse(BaseModel):
    """Result of dispatching a test ping payload to a webhook destination."""

    success: bool
    status_code: int
    message: str
    response_body: Optional[str] = None
    error: Optional[str] = None
