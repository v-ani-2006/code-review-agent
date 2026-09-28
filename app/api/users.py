import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ApiResponse
from app.schemas.user import UserProfileResponse, UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get(
    "/profile",
    response_model=ApiResponse[UserProfileResponse],
    summary="Get Detailed User Profile",
    description="Returns detailed profile information and review activity statistics for authenticated user.",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[UserProfileResponse]:
    """Retrieve detailed user profile."""
    profile = await user_service.get_user_profile(db, current_user)
    return ApiResponse(
        success=True,
        message="User profile retrieved successfully.",
        data=profile,
    )


@router.put(
    "/profile",
    response_model=ApiResponse[UserResponse],
    summary="Update Profile Details",
    description="Update mutable attributes like display name for currently authenticated user.",
)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[UserResponse]:
    """Update profile attributes."""
    updated = await user_service.update_profile(db, current_user, update_data)
    return ApiResponse(
        success=True,
        message="Profile updated successfully.",
        data=UserResponse.model_validate(updated),
    )


@router.delete(
    "/profile",
    response_model=ApiResponse[None],
    summary="Deactivate Own Account",
    description="Performs soft deletion of user account by setting is_active to false.",
)
async def deactivate_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[None]:
    """Deactivate authenticated account."""
    await user_service.deactivate_account(db, current_user)
    return ApiResponse(
        success=True,
        message="Account has been successfully deactivated.",
        data=None,
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Get User By ID",
    description="Fetch public user account metadata by UUID.",
)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[UserResponse]:
    """Look up a user account by primary key UUID."""
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' was not found.",
        )
    return ApiResponse(
        success=True,
        message="User found.",
        data=UserResponse.model_validate(user),
    )


@router.get(
    "",
    response_model=ApiResponse[List[UserResponse]],
    summary="List All Users (Admin Only)",
    description="Administrative endpoint returning paginated registered users. Requires is_admin=True.",
)
async def list_users(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0, description="Offset pagination"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum users to return"),
) -> ApiResponse[List[UserResponse]]:
    """Admin-only endpoint to list all users."""
    users = await user_service.get_all_users(db, skip=skip, limit=limit)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(users)} user accounts.",
        data=[UserResponse.model_validate(u) for u in users],
    )
