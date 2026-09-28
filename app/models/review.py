import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Review(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Review entity representing automated and stored code reviews."""

    __tablename__ = "reviews"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    readability_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    security_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    complexity_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    maintainability_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Phase 6: Gemini AI Generated Insights & Artifacts
    ai_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_strengths: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_recommendations: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_bugfix: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_documentation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_test_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    ai_processing_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    ai_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Phase 7: AI Documentation, Generator & Export Artifacts
    documentation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    docstrings: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    readme_markdown: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    unit_tests: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    refactored_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    architecture_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    changelog: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    export_markdown: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    export_html: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Phase 8: History, Analytics, Tags, Status & Soft Delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_viewed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    tags: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    language_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    analysis_duration: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,
        index=True,
    )
    review_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Bidirectional relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reviews",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id} filename='{self.filename}' language='{self.language}' overall_score={self.overall_score}>"
