import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base shared user attributes."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username handle",
        examples=["alice_dev"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique electronic mail address",
        examples=["alice@example.com"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Full display name",
        examples=["Alice Johnson"],
    )


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(
        ...,
        min_length=8,
        description="Raw plaintext password to be hashed",
        examples=["StrongP@ssw0rd!"],
    )


class UserUpdate(BaseModel):
    """Schema for updating user details."""

    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class UserResponse(UserBase):
    """Schema for returning user data (excluding password hash)."""

    id: uuid.UUID = Field(..., description="Unique user identifier")
    is_active: bool = Field(..., description="Whether user account is active")
    is_admin: bool = Field(..., description="Whether user has administrative privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last account update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "alice_dev",
                "email": "alice@example.com",
                "full_name": "Alice Johnson",
                "is_active": True,
                "is_admin": False,
                "created_at": "2026-09-27T21:00:00Z",
                "updated_at": "2026-09-27T21:00:00Z",
            }
        },
    )


class UserProfileResponse(UserResponse):
    """Detailed profile response including activity statistics."""

    total_reviews: int = Field(default=0, description="Total number of code reviews created by this user")
