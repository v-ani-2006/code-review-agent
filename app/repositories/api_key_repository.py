from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey
from app.repositories.base_repository import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository managing lifecycle and queries for APIKey entities."""

    def __init__(self):
        super().__init__(APIKey)

    async def create_api_key(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        hashed_key: str,
        prefix: str,
        permissions: List[str],
        expires_at: Optional[datetime] = None,
    ) -> APIKey:
        """Create and persist a new APIKey."""
        return await self.create(
            db,
            user_id=user_id,
            name=name,
            hashed_key=hashed_key,
            prefix=prefix,
            permissions=permissions,
            expires_at=expires_at,
            is_active=True,
            last_used_at=None,
        )

    async def get_by_hashed_key(self, db: AsyncSession, hashed_key: str) -> Optional[APIKey]:
        """Lookup active APIKey by its secure cryptographic hash."""
        stmt = select(APIKey).where(
            and_(
                APIKey.hashed_key == hashed_key,
                APIKey.is_active == True,
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[APIKey], int]:
        """List API keys owned by a specific user with pagination."""
        count_stmt = select(func.count(APIKey.id)).where(APIKey.user_id == user_id)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def list_all(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[APIKey], int]:
        """Admin listing of all system API keys with pagination."""
        count_stmt = select(func.count(APIKey.id))
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(APIKey)
            .order_by(APIKey.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def update_last_used(self, db: AsyncSession, key_id: uuid.UUID) -> None:
        """Update last_used_at timestamp on successful authentication."""
        stmt = (
            update(APIKey)
            .where(APIKey.id == key_id)
            .values(last_used_at=datetime.now(timezone.utc))
        )
        await db.execute(stmt)
        await db.commit()

    async def update_key(
        self,
        db: AsyncSession,
        key_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        permissions: Optional[List[str]] = None,
    ) -> Optional[APIKey]:
        """Modify name, active state, or permission scopes of an API key."""
        filters = [APIKey.id == key_id]
        if not is_admin and user_id:
            filters.append(APIKey.user_id == user_id)

        stmt = select(APIKey).where(and_(*filters))
        result = await db.execute(stmt)
        key_obj = result.scalars().first()
        if not key_obj:
            return None

        if name is not None:
            key_obj.name = name
        if is_active is not None:
            key_obj.is_active = is_active
        if permissions is not None:
            key_obj.permissions = permissions

        await db.commit()
        await db.refresh(key_obj)
        return key_obj

    async def delete_key(
        self,
        db: AsyncSession,
        key_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
    ) -> bool:
        """Permanently delete an API key."""
        filters = [APIKey.id == key_id]
        if not is_admin and user_id:
            filters.append(APIKey.user_id == user_id)

        stmt = select(APIKey).where(and_(*filters))
        result = await db.execute(stmt)
        key_obj = result.scalars().first()
        if not key_obj:
            return False

        await db.delete(key_obj)
        await db.commit()
        return True


api_key_repository = APIKeyRepository()
