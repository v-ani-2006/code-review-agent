import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import PasswordChangeRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    """Service encapsulating authentication, registration, token lifecycles, and credential operations."""

    async def register_user(self, db: AsyncSession, register_data: RegisterRequest) -> User:
        """Register a new user account with duplicate checks and bcrypt hashing."""
        # 1. Check for existing username
        existing_username = await user_repository.get_by_username(db, register_data.username)
        if existing_username:
            logger.warning("Registration failed: Username '%s' already exists", register_data.username)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this username already exists.",
            )

        # 2. Check for existing email
        existing_email = await user_repository.get_by_email(db, register_data.email)
        if existing_email:
            logger.warning("Registration failed: Email '%s' already registered", register_data.email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        # 3. Hash password and create record
        password_hash = get_password_hash(register_data.password)
        new_user = await user_repository.create(
            db,
            username=register_data.username.strip(),
            email=register_data.email.lower().strip(),
            password_hash=password_hash,
            full_name=register_data.full_name.strip() if register_data.full_name else None,
            is_active=True,
            is_admin=False,
        )

        logger.info("Registration success: User '%s' (%s) registered successfully", new_user.username, new_user.id)
        return new_user

    async def authenticate_user(
        self,
        db: AsyncSession,
        username_or_email: str,
        password: str,
    ) -> User:
        """Authenticate user by either email or username with timing-safe password verification."""
        identifier = username_or_email.strip()

        # Check if identifier looks like an email or search both
        if "@" in identifier:
            user = await user_repository.get_by_email(db, identifier)
        else:
            user = await user_repository.get_by_username(db, identifier)

        # Fallback check
        if not user and "@" not in identifier:
            user = await user_repository.get_by_email(db, identifier)

        if not user or not verify_password(password, user.password_hash):
            logger.warning("Failed login attempt for identifier: %s", identifier)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning("Login rejected: Inactive user '%s' attempted login", user.username)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is deactivated. Please contact an administrator.",
            )

        logger.info("Login success: User '%s' authenticated successfully", user.username)
        return user

    def generate_tokens(self, user: User) -> TokenResponse:
        """Issue a pair of JWT access and refresh tokens for an authenticated user."""
        token_payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

        access_token = create_access_token(data=token_payload)
        refresh_token = create_refresh_token(data=token_payload)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def refresh_access_token(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue a fresh pair of tokens."""
        payload = verify_token(refresh_token, expected_type="refresh")
        user_id_str = payload.get("sub") or payload.get("user_id")

        try:
            user_uuid = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload identifier.",
            )

        user = await user_repository.get_by_id(db, user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User associated with refresh token no longer exists.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated.",
            )

        logger.info("Token refresh: Successfully issued new tokens for user '%s'", user.username)
        return self.generate_tokens(user)

    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        password_data: PasswordChangeRequest,
    ) -> bool:
        """Verify existing password and set a new hashed password."""
        if not verify_password(password_data.current_password, user.password_hash):
            logger.warning("Password change failed: Incorrect current password for '%s'", user.username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password entered is incorrect.",
            )

        if password_data.current_password == password_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password.",
            )

        user.password_hash = get_password_hash(password_data.new_password)
        await db.commit()
        await db.refresh(user)

        logger.info("Password change success: User '%s' updated their credentials", user.username)
        return True

    async def logout_user(self, user: User) -> bool:
        """Placeholder for token invalidation / distributed blacklist (e.g. Redis)."""
        logger.info("User logout: Session ended for user '%s'", user.username)
        return True


# Singleton instance
auth_service = AuthService()
