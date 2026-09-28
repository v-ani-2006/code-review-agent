from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.upload import Upload
from app.repositories.base_repository import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    """Repository handling database operations for uploaded files and archives."""

    def __init__(self):
        super().__init__(Upload)

    async def create_upload(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        original_filename: str,
        stored_filename: str,
        file_size: int,
        file_hash: str,
        mime_type: str = "text/x-python",
        language: str = "python",
        review_id: Optional[uuid.UUID] = None,
    ) -> Upload:
        """Create and persist a new Upload record."""
        return await self.create(
            db,
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=mime_type,
            language=language,
            review_id=review_id,
        )

    async def get_by_hash(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        file_hash: str,
    ) -> Optional[Upload]:
        """Find an existing upload by SHA-256 hash belonging to the specified user."""
        stmt = (
            select(Upload)
            .where(and_(Upload.user_id == user_id, Upload.file_hash == file_hash))
            .order_by(Upload.uploaded_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_upload_by_id(
        self,
        db: AsyncSession,
        upload_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Upload]:
        """Fetch upload ensuring user authorization."""
        stmt = select(Upload).where(Upload.id == upload_id)
        if not is_admin:
            stmt = stmt.where(Upload.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def search_uploads(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        filename: Optional[str] = None,
        language: Optional[str] = None,
        file_hash: Optional[str] = None,
        review_id: Optional[uuid.UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_admin: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Upload], int]:
        """Search uploaded files matching multi-criteria filters."""
        conditions = []
        if not is_admin:
            conditions.append(Upload.user_id == user_id)

        if filename:
            conditions.append(Upload.original_filename.ilike(f"%{filename.strip()}%"))
        if language:
            conditions.append(func.lower(Upload.language) == language.lower().strip())
        if file_hash:
            conditions.append(Upload.file_hash == file_hash.strip())
        if review_id:
            conditions.append(Upload.review_id == review_id)
        if date_from:
            conditions.append(Upload.uploaded_at >= date_from)
        if date_to:
            conditions.append(Upload.uploaded_at <= date_to)

        count_stmt = select(func.count(Upload.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        stmt = select(Upload)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Upload.uploaded_at.desc()).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        return list(result.scalars().all()), total


upload_repository = UploadRepository()
