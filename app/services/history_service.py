from datetime import datetime
import difflib
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.user import User
from app.repositories.history_repository import history_repository
from app.schemas.history import (
    ComparisonResponse,
    HistoryDetailResponse,
    HistoryItem,
    HistoryListResponse,
    PaginationMeta,
    ScoreDiff,
    TimelineGroup,
    TimelineResponse,
)


class HistoryService:
    """Business logic for code review history, search, favorites, lifecycle, and comparisons."""

    async def list_history(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> HistoryListResponse:
        """Query paginated review history with filtering and sorting."""
        reviews, total_items, total_pages = await history_repository.get_history(
            db=db,
            user_id=user.id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            is_admin=user.is_admin,
        )

        logger.info("History viewed: user=%s, page=%s, total=%s", user.username, page, total_items)
        items = [HistoryItem.model_validate(r) for r in reviews]
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return HistoryListResponse(success=True, items=items, meta=meta)

    async def get_review_detail(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user: User,
    ) -> HistoryDetailResponse:
        """Fetch exhaustive review detail and increment view counter."""
        review = await history_repository.get_review_by_id(
            db=db,
            review_id=review_id,
            user_id=user.id,
            is_admin=user.is_admin,
            include_deleted=False,
        )
        if not review:
            logger.warning("Review detail not found or unauthorized: id=%s user=%s", review_id, user.username)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' was not found or has been deleted.",
            )

        # Track view count & timestamp
        review = await history_repository.increment_view_count(db, review)
        logger.info("Review viewed: id=%s user=%s view_count=%s", review_id, user.username, review.view_count)
        return HistoryDetailResponse.model_validate(review)

    async def toggle_favorite(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user: User,
        favorite_state: Optional[bool] = None,
    ) -> HistoryItem:
        """Toggle or explicitly set favorite flag on a review."""
        review = await history_repository.favorite_review(
            db=db,
            review_id=review_id,
            user_id=user.id,
            is_admin=user.is_admin,
            state=favorite_state,
        )
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found.",
            )
        logger.info("Favorite updated: id=%s user=%s favorite=%s", review_id, user.username, review.favorite)
        try:
            import asyncio
            from app.core.audit import log_audit_background
            from app.services.cache_service import cache_service
            await cache_service.invalidate_review(review_id, user.id)
            asyncio.create_task(
                log_audit_background(
                    action="review.favorite_changed",
                    resource="review",
                    user_id=user.id,
                    resource_id=str(review_id),
                    metadata={"favorite": review.favorite},
                )
            )
        except Exception:
            pass
        return HistoryItem.model_validate(review)

    async def soft_delete_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user: User,
    ) -> Dict[str, Any]:
        """Soft delete a review record."""
        review = await history_repository.soft_delete_review(
            db=db,
            review_id=review_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found or already deleted.",
            )
        logger.info("Review deleted (soft): id=%s user=%s", review_id, user.username)
        try:
            import asyncio
            from app.core.audit import log_audit_background
            from app.services.cache_service import cache_service
            await cache_service.invalidate_review(review_id, user.id)
            asyncio.create_task(
                log_audit_background(
                    action="review.deleted",
                    resource="review",
                    user_id=user.id,
                    resource_id=str(review_id),
                )
            )
        except Exception:
            pass
        return {
            "success": True,
            "message": f"Review '{review_id}' successfully moved to trash.",
            "deleted_at": review.deleted_at,
        }

    async def restore_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user: User,
    ) -> Dict[str, Any]:
        """Restore a soft-deleted review from trash."""
        review = await history_repository.restore_review(
            db=db,
            review_id=review_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' is not in trash or could not be found.",
            )
        logger.info("Review restored: id=%s user=%s", review_id, user.username)
        try:
            import asyncio
            from app.core.audit import log_audit_background
            from app.services.cache_service import cache_service
            await cache_service.invalidate_review(review_id, user.id)
            asyncio.create_task(
                log_audit_background(
                    action="review.restored",
                    resource="review",
                    user_id=user.id,
                    resource_id=str(review_id),
                )
            )
        except Exception:
            pass
        return {
            "success": True,
            "message": f"Review '{review_id}' successfully restored.",
            "review": HistoryItem.model_validate(review),
        }


    async def archive_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user: User,
    ) -> HistoryItem:
        """Archive a review."""
        review = await history_repository.archive_review(
            db=db,
            review_id=review_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found.",
            )
        logger.info("Review archived: id=%s user=%s", review_id, user.username)
        return HistoryItem.model_validate(review)

    async def get_recent(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 10,
    ) -> List[HistoryItem]:
        """Fetch recently analyzed active reviews."""
        reviews = await history_repository.get_recent_reviews(
            db=db,
            user_id=user.id,
            limit=limit,
            is_admin=user.is_admin,
        )
        return [HistoryItem.model_validate(r) for r in reviews]

    async def get_favorites(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> HistoryListResponse:
        """Fetch paginated favorite reviews."""
        return await self.list_history(
            db=db,
            user=user,
            page=page,
            page_size=page_size,
            filters={"favorite": True},
        )

    async def get_trash(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> HistoryListResponse:
        """Fetch paginated soft-deleted reviews."""
        return await self.list_history(
            db=db,
            user=user,
            page=page,
            page_size=page_size,
            filters={"only_deleted": True},
        )

    async def search(
        self,
        db: AsyncSession,
        user: User,
        query: str,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> HistoryListResponse:
        """Search reviews matching partial filename, summary, language, code, or UUID."""
        if not query or not query.strip():
            return await self.list_history(db, user, page=page, page_size=page_size, filters=filters)

        reviews, total_items, total_pages = await history_repository.search_reviews(
            db=db,
            user_id=user.id,
            query=query,
            page=page,
            page_size=page_size,
            filters=filters,
            is_admin=user.is_admin,
        )
        logger.info("Search performed: query='%s' user=%s results=%s", query, user.username, total_items)
        items = [HistoryItem.model_validate(r) for r in reviews]
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return HistoryListResponse(success=True, items=items, meta=meta)

    async def get_by_language(
        self,
        db: AsyncSession,
        user: User,
        language: str,
        page: int = 1,
        page_size: int = 20,
    ) -> HistoryListResponse:
        """Filter review history by programming language."""
        return await self.list_history(
            db=db,
            user=user,
            page=page,
            page_size=page_size,
            filters={"language": language},
        )

    async def get_by_score(
        self,
        db: AsyncSession,
        user: User,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> HistoryListResponse:
        """Filter review history by score range."""
        return await self.list_history(
            db=db,
            user=user,
            page=page,
            page_size=page_size,
            filters={"min_score": min_score, "max_score": max_score},
        )

    async def get_by_date(
        self,
        db: AsyncSession,
        user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> HistoryListResponse:
        """Filter review history by created date range."""
        return await self.list_history(
            db=db,
            user=user,
            page=page,
            page_size=page_size,
            filters={"date_from": start_date, "date_to": end_date},
        )

    async def get_timeline(
        self,
        db: AsyncSession,
        user: User,
        group_by: str = "day",
    ) -> TimelineResponse:
        """Group historical reviews chronologically into day, week, or month blocks."""
        valid_groupings = {"day", "week", "month"}
        if group_by.lower() not in valid_groupings:
            group_by = "day"

        raw_timeline = await history_repository.get_timeline(
            db=db,
            user_id=user.id,
            group_by=group_by.lower(),
            is_admin=user.is_admin,
        )

        timeline_groups = [
            TimelineGroup(
                period=g["period"],
                count=g["count"],
                average_score=g["average_score"],
                reviews=[HistoryItem.model_validate(r) for r in g["reviews"]],
            )
            for g in raw_timeline
        ]
        total_revs = sum(g.count for g in timeline_groups)
        return TimelineResponse(
            success=True,
            group_by=group_by.lower(),
            total_reviews=total_revs,
            timeline=timeline_groups,
        )

    async def compare_reviews(
        self,
        db: AsyncSession,
        user: User,
        review_id_a: uuid.UUID,
        review_id_b: uuid.UUID,
    ) -> ComparisonResponse:
        """Generate structured analytical comparison and code difference between two reviews."""
        review_a = await history_repository.get_review_by_id(
            db=db,
            review_id=review_id_a,
            user_id=user.id,
            is_admin=user.is_admin,
            include_deleted=True,
        )
        if not review_a:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baseline review '{review_id_a}' not found.",
            )

        review_b = await history_repository.get_review_by_id(
            db=db,
            review_id=review_id_b,
            user_id=user.id,
            is_admin=user.is_admin,
            include_deleted=True,
        )
        if not review_b:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comparison review '{review_id_b}' not found.",
            )

        # Compute metric score diffs
        metrics = [
            ("Overall Score", review_a.overall_score, review_b.overall_score),
            ("Security Score", review_a.security_score, review_b.security_score),
            ("Complexity Score", review_a.complexity_score, review_b.complexity_score),
            ("Readability Score", review_a.readability_score, review_b.readability_score),
            ("Maintainability Score", review_a.maintainability_score, review_b.maintainability_score),
        ]

        score_diffs = []
        improvements = 0
        total_metrics = 0
        for name, sa, sb in metrics:
            if sa is not None and sb is not None:
                diff = round(sb - sa, 2)
                improved = diff > 0
                if improved:
                    improvements += 1
                total_metrics += 1
            else:
                diff = None
                improved = None

            score_diffs.append(
                ScoreDiff(
                    metric=name,
                    score_a=sa,
                    score_b=sb,
                    difference=diff,
                    improved=improved,
                )
            )

        # Code Diff analysis
        lines_a = (review_a.source_code or "").splitlines()
        lines_b = (review_b.source_code or "").splitlines()
        matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
        similarity_ratio = round(matcher.ratio() * 100, 1)

        diff_lines = list(difflib.unified_diff(
            lines_a, lines_b,
            fromfile=f"a/{review_a.filename}",
            tofile=f"b/{review_b.filename}",
            lineterm="",
        ))

        summary_diff = {
            "review_a_summary": review_a.summary or review_a.ai_summary or "No summary available.",
            "review_b_summary": review_b.summary or review_b.ai_summary or "No summary available.",
            "code_similarity_percentage": similarity_ratio,
        }

        structural_diff = {
            "lines_count_a": len(lines_a),
            "lines_count_b": len(lines_b),
            "delta_lines": len(lines_b) - len(lines_a),
            "unified_diff_sample": diff_lines[:30],
            "total_diff_lines": len(diff_lines),
        }

        if improvements > (total_metrics / 2):
            verdict = "Review B demonstrates overall quality improvement over Review A with higher metric scores."
        elif improvements < (total_metrics / 2) and total_metrics > 0:
            verdict = "Review A scored higher than Review B; quality regressed on measured metrics."
        else:
            verdict = "Both reviews exhibit comparable code quality and performance characteristics."

        logger.info(
            "Comparison generated: review_a=%s review_b=%s user=%s verdict='%s'",
            review_id_a,
            review_id_b,
            user.username,
            verdict,
        )

        return ComparisonResponse(
            success=True,
            review_a=HistoryItem.model_validate(review_a),
            review_b=HistoryItem.model_validate(review_b),
            score_diffs=score_diffs,
            summary_diff=summary_diff,
            structural_diff=structural_diff,
            verdict=verdict,
        )


history_service = HistoryService()
