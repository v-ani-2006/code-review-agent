import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.review import Review
from app.repositories.base_repository import BaseRepository


class HistoryRepository(BaseRepository[Review]):
    """Repository handling database operations for review history, search, and lifecycle."""

    def __init__(self):
        super().__init__(Review)

    async def get_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
        is_admin: bool = False,
    ) -> Tuple[List[Review], int, int]:
        """Fetch paginated, filtered, and sorted review history."""
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        filters = filters or {}

        conditions = []

        # Access control
        if not is_admin:
            conditions.append(Review.user_id == user_id)

        # Soft delete handling
        include_deleted = filters.get("include_deleted", False)
        only_deleted = filters.get("only_deleted", False)
        if only_deleted:
            conditions.append(Review.is_deleted.is_(True))
        elif not include_deleted:
            conditions.append(Review.is_deleted.is_(False))

        # Explicit filters
        if filters.get("language"):
            conditions.append(func.lower(Review.language) == filters["language"].lower().strip())
        if filters.get("favorite") is not None:
            conditions.append(Review.favorite == filters["favorite"])
        if filters.get("status"):
            conditions.append(func.lower(Review.status) == filters["status"].lower().strip())
        if filters.get("filename"):
            conditions.append(Review.filename.ilike(f"%{filters['filename'].strip()}%"))

        # Score range filters
        if filters.get("min_score") is not None:
            conditions.append(Review.overall_score >= float(filters["min_score"]))
        if filters.get("max_score") is not None:
            conditions.append(Review.overall_score <= float(filters["max_score"]))
        if filters.get("complexity_min") is not None:
            conditions.append(Review.complexity_score >= float(filters["complexity_min"]))
        if filters.get("complexity_max") is not None:
            conditions.append(Review.complexity_score <= float(filters["complexity_max"]))
        if filters.get("security_min") is not None:
            conditions.append(Review.security_score >= float(filters["security_min"]))
        if filters.get("security_max") is not None:
            conditions.append(Review.security_score <= float(filters["security_max"]))
        if filters.get("maintainability_min") is not None:
            conditions.append(Review.maintainability_score >= float(filters["maintainability_min"]))
        if filters.get("maintainability_max") is not None:
            conditions.append(Review.maintainability_score <= float(filters["maintainability_max"]))

        # Date range filters
        if filters.get("date_from"):
            conditions.append(Review.created_at >= filters["date_from"])
        if filters.get("date_to"):
            conditions.append(Review.created_at <= filters["date_to"])
        if filters.get("updated_from"):
            conditions.append(Review.updated_at >= filters["updated_from"])
        if filters.get("updated_to"):
            conditions.append(Review.updated_at <= filters["updated_to"])

        # Processing time range filters
        if filters.get("processing_time_min") is not None:
            conditions.append(Review.ai_processing_time >= float(filters["processing_time_min"]))
        if filters.get("processing_time_max") is not None:
            conditions.append(Review.ai_processing_time <= float(filters["processing_time_max"]))

        # Count total matching rows
        count_stmt = select(func.count()).select_from(Review)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_items_res = await db.execute(count_stmt)
        total_items = total_items_res.scalar_one() or 0

        # Sort mapping
        sort_column_map = {
            "created_at": Review.created_at,
            "updated_at": Review.updated_at,
            "overall_score": Review.overall_score,
            "security_score": Review.security_score,
            "complexity_score": Review.complexity_score,
            "readability_score": Review.readability_score,
            "maintainability_score": Review.maintainability_score,
            "filename": Review.filename,
            "language": Review.language,
            "processing_time": Review.ai_processing_time,
            "view_count": Review.view_count,
        }
        order_col = sort_column_map.get(sort_by, Review.created_at)
        order_clause = order_col.asc() if sort_order.lower() == "asc" else order_col.desc()

        # Query items
        stmt = select(Review)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(order_clause).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())
        total_pages = max(1, math.ceil(total_items / page_size))

        return items, total_items, total_pages

    async def get_review_by_id(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
        include_deleted: bool = False,
    ) -> Optional[Review]:
        """Fetch a specific review by ID ensuring ownership or admin privilege."""
        stmt = select(Review).where(Review.id == review_id)
        if not is_admin:
            stmt = stmt.where(Review.user_id == user_id)
        if not include_deleted:
            stmt = stmt.where(Review.is_deleted.is_(False))

        result = await db.execute(stmt)
        return result.scalars().first()

    async def search_reviews(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        query: str,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        is_admin: bool = False,
    ) -> Tuple[List[Review], int, int]:
        """Perform partial match search across filenames, summaries, languages, source code, and tags."""
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        filters = filters or {}
        q = f"%{query.strip()}%"

        search_or_terms = [
            Review.filename.ilike(q),
            Review.language.ilike(q),
            Review.summary.ilike(q),
            Review.ai_summary.ilike(q),
            Review.source_code.ilike(q),
            Review.ai_recommendations.ilike(q),
        ]

        # Check if query matches a valid UUID
        try:
            val_uuid = uuid.UUID(query.strip())
            search_or_terms.append(Review.id == val_uuid)
        except ValueError:
            pass

        conditions = [or_(*search_or_terms)]

        # Access control
        if not is_admin:
            conditions.append(Review.user_id == user_id)

        # Soft delete handling
        include_deleted = filters.get("include_deleted", False)
        if not include_deleted:
            conditions.append(Review.is_deleted.is_(False))

        if filters.get("language"):
            conditions.append(func.lower(Review.language) == filters["language"].lower().strip())
        if filters.get("favorite") is not None:
            conditions.append(Review.favorite == filters["favorite"])
        if filters.get("status"):
            conditions.append(func.lower(Review.status) == filters["status"].lower().strip())
        if filters.get("min_score") is not None:
            conditions.append(Review.overall_score >= float(filters["min_score"]))
        if filters.get("max_score") is not None:
            conditions.append(Review.overall_score <= float(filters["max_score"]))
        if filters.get("date_from"):
            conditions.append(Review.created_at >= filters["date_from"])
        if filters.get("date_to"):
            conditions.append(Review.created_at <= filters["date_to"])

        # Count
        count_stmt = select(func.count()).select_from(Review).where(and_(*conditions))
        total_items_res = await db.execute(count_stmt)
        total_items = total_items_res.scalar_one() or 0

        # Query
        stmt = (
            select(Review)
            .where(and_(*conditions))
            .order_by(Review.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        total_pages = max(1, math.ceil(total_items / page_size))

        return items, total_items, total_pages

    async def favorite_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
        state: Optional[bool] = None,
    ) -> Optional[Review]:
        """Toggle or set favorite status for a review."""
        review = await self.get_review_by_id(db, review_id, user_id, is_admin=is_admin)
        if not review:
            return None

        if state is None:
            review.favorite = not review.favorite
        else:
            review.favorite = state

        await db.commit()
        await db.refresh(review)
        logger.info("Review %s favorite set to %s by user %s", review_id, review.favorite, user_id)
        return review

    async def soft_delete_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Review]:
        """Soft-delete a review by flagging is_deleted and recording deletion timestamp."""
        review = await self.get_review_by_id(db, review_id, user_id, is_admin=is_admin, include_deleted=False)
        if not review:
            return None

        review.is_deleted = True
        review.deleted_at = datetime.now(timezone.utc)
        review.status = "deleted"
        await db.commit()
        await db.refresh(review)
        logger.info("Review %s soft-deleted by user %s", review_id, user_id)
        return review

    async def restore_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Review]:
        """Restore a soft-deleted review back to active history."""
        review = await self.get_review_by_id(db, review_id, user_id, is_admin=is_admin, include_deleted=True)
        if not review or not review.is_deleted:
            return None

        review.is_deleted = False
        review.deleted_at = None
        review.status = "completed"
        await db.commit()
        await db.refresh(review)
        logger.info("Review %s restored from trash by user %s", review_id, user_id)
        return review

    async def archive_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Review]:
        """Archive a review without deleting it."""
        review = await self.get_review_by_id(db, review_id, user_id, is_admin=is_admin)
        if not review:
            return None

        review.status = "archived"
        await db.commit()
        await db.refresh(review)
        logger.info("Review %s archived by user %s", review_id, user_id)
        return review

    async def increment_view_count(
        self,
        db: AsyncSession,
        review: Review,
    ) -> Review:
        """Increment inspection view counter and update last_viewed timestamp."""
        review.view_count = (review.view_count or 0) + 1
        review.last_viewed = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(review)
        return review

    async def get_recent_reviews(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 10,
        is_admin: bool = False,
    ) -> List[Review]:
        """Fetch recently analyzed active reviews."""
        stmt = select(Review).where(Review.is_deleted.is_(False))
        if not is_admin:
            stmt = stmt.where(Review.user_id == user_id)
        stmt = stmt.order_by(Review.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_timeline(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        group_by: str = "day",
        is_admin: bool = False,
    ) -> List[Dict[str, Any]]:
        """Fetch chronological reviews grouped by period (day, week, or month)."""
        stmt = select(Review).where(Review.is_deleted.is_(False))
        if not is_admin:
            stmt = stmt.where(Review.user_id == user_id)
        stmt = stmt.order_by(Review.created_at.desc())
        result = await db.execute(stmt)
        reviews = list(result.scalars().all())

        groups: Dict[str, List[Review]] = {}
        for r in reviews:
            dt = r.created_at
            if group_by == "month":
                period_key = dt.strftime("%Y-%m")
            elif group_by == "week":
                period_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            else:
                period_key = dt.strftime("%Y-%m-%d")

            if period_key not in groups:
                groups[period_key] = []
            groups[period_key].append(r)

        timeline_output = []
        for period, revs in groups.items():
            valid_scores = [rv.overall_score for rv in revs if rv.overall_score is not None]
            avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else None
            timeline_output.append(
                {
                    "period": period,
                    "count": len(revs),
                    "average_score": avg_score,
                    "reviews": revs,
                }
            )

        return timeline_output


history_repository = HistoryRepository()
