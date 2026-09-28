from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.history import (
    ComparisonResponse,
    HistoryDetailResponse,
    HistoryItem,
    HistoryListResponse,
    ReviewCompareRequest,
    TimelineResponse,
)
from app.services.history_service import history_service

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Review History",
    description="Retrieve paginated review history with multi-criteria filtering, sorting, and user-scoping.",
)
async def list_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort attribute"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    language: Optional[str] = Query(None, description="Filter by language"),
    favorite: Optional[bool] = Query(None, description="Filter by favorite flag"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (completed, archived)"),
    filename: Optional[str] = Query(None, description="Filter by filename substring"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum overall score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum overall score"),
    complexity_min: Optional[float] = Query(None, description="Minimum complexity score"),
    complexity_max: Optional[float] = Query(None, description="Maximum complexity score"),
    security_min: Optional[float] = Query(None, description="Minimum security score"),
    security_max: Optional[float] = Query(None, description="Maximum security score"),
    maintainability_min: Optional[float] = Query(None, description="Minimum maintainability score"),
    maintainability_max: Optional[float] = Query(None, description="Maximum maintainability score"),
    date_from: Optional[datetime] = Query(None, description="Filter creation starting from"),
    date_to: Optional[datetime] = Query(None, description="Filter creation up to"),
    updated_from: Optional[datetime] = Query(None, description="Filter update starting from"),
    updated_to: Optional[datetime] = Query(None, description="Filter update up to"),
    processing_time_min: Optional[float] = Query(None, description="Minimum AI analysis time"),
    processing_time_max: Optional[float] = Query(None, description="Maximum AI analysis time"),
) -> HistoryListResponse:
    """List code review history records."""
    filters = {
        "language": language,
        "favorite": favorite,
        "status": status_filter,
        "filename": filename,
        "min_score": min_score,
        "max_score": max_score,
        "complexity_min": complexity_min,
        "complexity_max": complexity_max,
        "security_min": security_min,
        "security_max": security_max,
        "maintainability_min": maintainability_min,
        "maintainability_max": maintainability_max,
        "date_from": date_from,
        "date_to": date_to,
        "updated_from": updated_from,
        "updated_to": updated_to,
        "processing_time_min": processing_time_min,
        "processing_time_max": processing_time_max,
    }
    # Clean None filters
    clean_filters = {k: v for k, v in filters.items() if v is not None}
    return await history_service.list_history(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        filters=clean_filters,
    )


@router.get(
    "/recent",
    response_model=List[HistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get Recently Analyzed Reviews",
    description="Retrieve the latest N active reviews submitted by the user.",
)
async def get_recent_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = Query(10, ge=1, le=50, description="Max reviews to return"),
) -> List[HistoryItem]:
    """Retrieve recently analyzed reviews."""
    return await history_service.get_recent(db=db, user=current_user, limit=limit)


@router.get(
    "/favorites",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Favorite Reviews",
    description="Retrieve paginated list of reviews marked as favorite by the user.",
)
async def get_favorite_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> HistoryListResponse:
    """Retrieve user's favorite reviews."""
    return await history_service.get_favorites(db=db, user=current_user, page=page, page_size=page_size)


@router.get(
    "/trash",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Soft-Deleted Reviews",
    description="Retrieve paginated list of reviews currently in the trash.",
)
async def get_trash_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> HistoryListResponse:
    """Retrieve soft-deleted reviews."""
    return await history_service.get_trash(db=db, user=current_user, page=page, page_size=page_size)


@router.get(
    "/search",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Review History",
    description="Full-text and partial match search across filenames, summaries, languages, source code, and tags.",
)
async def search_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    q: str = Query("", description="Search search keyword or UUID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    language: Optional[str] = Query(None, description="Optional language filter"),
    favorite: Optional[bool] = Query(None, description="Optional favorite filter"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score"),
) -> HistoryListResponse:
    """Search code reviews."""
    filters = {}
    if language:
        filters["language"] = language
    if favorite is not None:
        filters["favorite"] = favorite
    if min_score is not None:
        filters["min_score"] = min_score
    if max_score is not None:
        filters["max_score"] = max_score

    return await history_service.search(
        db=db,
        user=current_user,
        query=q,
        page=page,
        page_size=page_size,
        filters=filters,
    )


@router.get(
    "/by-language/{language}",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Reviews By Language",
    description="Filter review history by specific programming language.",
)
async def get_by_language(
    language: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> HistoryListResponse:
    """Filter reviews by language."""
    return await history_service.get_by_language(db=db, user=current_user, language=language, page=page, page_size=page_size)


@router.get(
    "/by-score",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Reviews By Score Range",
    description="Filter reviews matching min and max overall score criteria.",
)
async def get_by_score(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> HistoryListResponse:
    """Filter reviews by score."""
    return await history_service.get_by_score(
        db=db,
        user=current_user,
        min_score=min_score,
        max_score=max_score,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/by-date",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Reviews By Date Range",
    description="Filter reviews submitted between start_date and end_date.",
)
async def get_by_date(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: Optional[datetime] = Query(None, description="Start date/time"),
    end_date: Optional[datetime] = Query(None, description="End date/time"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> HistoryListResponse:
    """Filter reviews by date."""
    return await history_service.get_by_date(
        db=db,
        user=current_user,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Two Reviews (POST)",
    description="Perform structured side-by-side metric comparison and code diff between two reviews.",
)
async def compare_reviews_post(
    request: ReviewCompareRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ComparisonResponse:
    """Compare two reviews via request body."""
    return await history_service.compare_reviews(
        db=db,
        user=current_user,
        review_id_a=request.review_id_a,
        review_id_b=request.review_id_b,
    )


@router.get(
    "/compare/{review_a}/{review_b}",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Two Reviews (GET)",
    description="Perform structured comparison between two reviews via path parameters.",
)
async def compare_reviews_get(
    review_a: uuid.UUID,
    review_b: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ComparisonResponse:
    """Compare two reviews via path IDs."""
    return await history_service.compare_reviews(
        db=db,
        user=current_user,
        review_id_a=review_a,
        review_id_b=review_b,
    )


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Review Timeline",
    description="Retrieve chronological review history grouped by day, week, or month.",
)
async def get_timeline(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    group_by: str = Query("day", pattern="^(day|week|month)$", description="Timeline bucket interval"),
) -> TimelineResponse:
    """Retrieve review timeline."""
    return await history_service.get_timeline(db=db, user=current_user, group_by=group_by)


@router.get(
    "/{review_id}",
    response_model=HistoryDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Review Detail",
    description="Fetch full review detail including source code and AI artifacts. Increments view counter.",
)
async def get_review_detail(
    review_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> HistoryDetailResponse:
    """Retrieve single review detail."""
    return await history_service.get_review_detail(db=db, review_id=review_id, user=current_user)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft Delete Review",
    description="Mark a review as soft-deleted and move it to trash.",
)
async def delete_review(
    review_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Soft delete review."""
    return await history_service.soft_delete_review(db=db, review_id=review_id, user=current_user)


@router.patch(
    "/{review_id}/favorite",
    response_model=HistoryItem,
    status_code=status.HTTP_200_OK,
    summary="Toggle Favorite Review",
    description="Toggle or explicitly set the favorite flag on a review.",
)
async def toggle_favorite(
    review_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    state: Optional[bool] = Query(None, description="Explicit favorite state (omit to toggle)"),
) -> HistoryItem:
    """Toggle favorite review status."""
    return await history_service.toggle_favorite(db=db, review_id=review_id, user=current_user, favorite_state=state)


@router.patch(
    "/{review_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restore Review from Trash",
    description="Restore a soft-deleted review back into active history.",
)
@router.post("/{review_id}/restore", status_code=status.HTTP_200_OK, include_in_schema=False)
async def restore_review(
    review_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Restore review from trash."""
    return await history_service.restore_review(db=db, review_id=review_id, user=current_user)


@router.patch(
    "/{review_id}/archive",
    response_model=HistoryItem,
    status_code=status.HTTP_200_OK,
    summary="Archive Review",
    description="Mark a review as archived.",
)
async def archive_review(
    review_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> HistoryItem:
    """Archive review."""
    return await history_service.archive_review(db=db, review_id=review_id, user=current_user)
