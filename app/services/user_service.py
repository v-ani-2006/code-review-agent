import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.review import Review
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserProfileResponse, UserUpdate


class UserService:
    """Service handling user account lifecycle, profile modifications, and admin lookups."""

    async def get_user_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Retrieve a user account by primary key UUID."""
        return await user_repository.get_by_id(db, user_id)

    async def get_user_profile(self, db: AsyncSession, user: User) -> UserProfileResponse:
        """Construct detailed user profile including review activity statistics."""
        # Calculate total reviews submitted by this user
        count_stmt = select(func.count(Review.id)).where(Review.user_id == user.id)
        count_result = await db.execute(count_stmt)
        total_reviews = count_result.scalar() or 0

        return UserProfileResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            total_reviews=total_reviews,
        )

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        update_data: UserUpdate,
    ) -> User:
        """Update mutable profile fields for the authenticated user."""
        update_fields = {}
        if update_data.full_name is not None:
            update_fields["full_name"] = update_data.full_name.strip()
        if update_data.is_active is not None:
            update_fields["is_active"] = update_data.is_active

        updated_user = await user_repository.update(db, user, update_fields)
        logger.info("User profile updated: User '%s' (%s)", user.username, user.id)
        return updated_user

    async def deactivate_account(self, db: AsyncSession, user: User) -> User:
        """Deactivate account (soft delete)."""
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        logger.info("User account deactivated: '%s' (%s)", user.username, user.id)
        return user

    async def activate_account(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Admin action: Reactivate a deactivated user account."""
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        logger.info("User account reactivated: '%s' (%s)", user.username, user.id)
        return user

    async def get_all_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """Admin query: Retrieve paginated list of all registered users."""
        return await user_repository.get_all(db, skip=skip, limit=limit)


# Singleton instance
user_service = UserService()
