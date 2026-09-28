from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreate(BaseModel):
    """Payload to create a new provisioned API key."""

    name: str = Field(..., description="Human-readable descriptive label for this key", min_length=1, max_length=100)
    permissions: List[str] = Field(
        default_factory=lambda: ["reviews:read", "reviews:write", "upload:write", "batch:write"],
        description="Allowed permission scopes for this key (e.g. ['reviews:read', 'batch:write'])",
    )
    expires_days: Optional[int] = Field(
        None,
        description="Optional expiration in days (leave null for non-expiring service keys)",
        ge=1,
        le=3650,
    )


class APIKeyUpdate(BaseModel):
    """Payload to update an API key's label, active status, or permissions."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None


class APIKeyResponse(BaseModel):
    """Safe representation of an API key without exposing the hashed secret."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    prefix: str
    is_active: bool
    permissions: List[str]
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreateResponse(BaseModel):
    """One-time response returning the plaintext API key secret."""

    success: bool = True
    raw_api_key: str = Field(..., description="Plaintext secret key. Save immediately; cannot be recovered.")
    key_info: APIKeyResponse
    warning: str = "Store this secret key securely. It will never be shown again."


class APIKeyListResponse(BaseModel):
    """Collection of managed API keys."""

    success: bool = True
    total: int
    keys: List[APIKeyResponse] = Field(default_factory=list)
