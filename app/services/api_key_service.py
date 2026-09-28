from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Tuple
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.api_key import APIKey
from app.models.user import User
from app.repositories.api_key_repository import api_key_repository
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyUpdate,
)


class APIKeyService:
    """Service managing cryptographically secure API keys, verification, and scopes."""

    @staticmethod
    def _hash_key(raw_key: str) -> str:
        """Compute SHA-256 hex digest of raw secret key for storage and lookup."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def create_api_key(
        self,
        db: AsyncSession,
        user: User,
        data: APIKeyCreate,
    ) -> APIKeyCreateResponse:
        """Generate a cryptographically secure random API key and persist only its hash."""
        random_part = secrets.token_urlsafe(32)
        raw_key = f"cp_live_{random_part}"
        prefix = raw_key[:14]
        hashed = self._hash_key(raw_key)

        expires_at = None
        if data.expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_days)

        key_obj = await api_key_repository.create_api_key(
            db=db,
            user_id=user.id,
            name=data.name,
            hashed_key=hashed,
            prefix=prefix,
            permissions=data.permissions,
            expires_at=expires_at,
        )

        logger.info(
            "🔑 Provisioned API key '%s' (prefix: %s) for user %s",
            data.name,
            prefix,
            user.username,
        )

        return APIKeyCreateResponse(
            raw_api_key=raw_key,
            key_info=APIKeyResponse.model_validate(key_obj),
        )

    async def list_user_keys(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> APIKeyListResponse:
        """List keys created by the authenticated user."""
        items, total = await api_key_repository.list_by_user(db=db, user_id=user.id, page=page, page_size=page_size)
        return APIKeyListResponse(
            total=total,
            keys=[APIKeyResponse.model_validate(k) for k in items],
        )

    async def list_all_keys(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> APIKeyListResponse:
        """Admin listing of all system API keys."""
        items, total = await api_key_repository.list_all(db=db, page=page, page_size=page_size)
        return APIKeyListResponse(
            total=total,
            keys=[APIKeyResponse.model_validate(k) for k in items],
        )

    async def update_key(
        self,
        db: AsyncSession,
        key_id: uuid.UUID,
        user: User,
        data: APIKeyUpdate,
    ) -> APIKeyResponse:
        """Update an API key's name, active state, or permission scopes."""
        updated = await api_key_repository.update_key(
            db=db,
            key_id=key_id,
            user_id=user.id,
            is_admin=user.is_admin,
            name=data.name,
            is_active=data.is_active,
            permissions=data.permissions,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key '{key_id}' not found.",
            )
        return APIKeyResponse.model_validate(updated)

    async def delete_key(
        self,
        db: AsyncSession,
        key_id: uuid.UUID,
        user: User,
    ) -> bool:
        """Permanently delete an API key."""
        deleted = await api_key_repository.delete_key(
            db=db,
            key_id=key_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key '{key_id}' not found.",
            )
        return True

    async def authenticate_api_key(
        self,
        db: AsyncSession,
        raw_key: str,
    ) -> Optional[Tuple[User, APIKey]]:
        """Verify API key hash, validity, and expiration; returns (User, APIKey) tuple."""
        hashed = self._hash_key(raw_key.strip())
        key_obj = await api_key_repository.get_by_hashed_key(db, hashed)
        if not key_obj:
            return None

        # Check expiration
        if key_obj.expires_at and datetime.now(timezone.utc) > key_obj.expires_at:
            logger.warning("Authentication failed: API key '%s' has expired.", key_obj.prefix)
            return None

        # Record usage
        await api_key_repository.update_last_used(db, key_obj.id)
        return key_obj.user, key_obj


api_key_service = APIKeyService()
