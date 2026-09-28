import re
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.schemas.user import UserResponse

T = TypeVar("T")


def validate_password_strength(password: str) -> str:
    """Enforce enterprise password complexity requirements:

    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter (A-Z).")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter (a-z).")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one numerical digit (0-9).")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/`~]", password):
        raise ValueError("Password must contain at least one special character (!@#$%^&*...).")
    return password


class RegisterRequest(BaseModel):
    """Schema for new user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric username (letters, numbers, underscore, hyphen)",
        examples=["alice_dev"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["alice@example.com"],
    )
    password: str = Field(
        ...,
        description="Secure password meeting complexity criteria",
        examples=["Secur3P@ssw0rd!"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional display name",
        examples=["Alice Johnson"],
    )

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        return validate_password_strength(v)


class LoginRequest(BaseModel):
    """Schema for user login with JSON payload."""

    username_or_email: str = Field(
        ...,
        description="Registered username or email address",
        examples=["alice_dev"],
    )
    password: str = Field(
        ...,
        description="Account password",
        examples=["Secur3P@ssw0rd!"],
    )


class TokenResponse(BaseModel):
    """Schema for successful token response."""

    access_token: str = Field(..., description="JWT access bearer token")
    refresh_token: str = Field(..., description="JWT long-lived refresh token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Access token expiration duration in seconds")
    user: UserResponse = Field(..., description="Authenticated user account details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "alice_dev",
                    "email": "alice@example.com",
                    "full_name": "Alice Johnson",
                    "is_active": True,
                    "is_admin": False,
                    "created_at": "2026-09-27T21:00:00Z",
                    "updated_at": "2026-09-27T21:00:00Z",
                },
            }
        }
    )


class RefreshRequest(BaseModel):
    """Schema for obtaining a new access token using a refresh token."""

    refresh_token: str = Field(..., description="Valid, unexpired refresh token")


class PasswordChangeRequest(BaseModel):
    """Schema for authenticated password change."""

    current_password: str = Field(..., description="Existing plaintext password")
    new_password: str = Field(..., description="New password meeting complexity criteria")

    @field_validator("new_password")
    @classmethod
    def check_new_password_complexity(cls, v: str) -> str:
        return validate_password_strength(v)


class ApiResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper."""

    success: bool = Field(default=True, description="Indicates operational success")
    message: str = Field(..., description="Contextual status or feedback message")
    data: Optional[T] = Field(default=None, description="Optional payload data")
