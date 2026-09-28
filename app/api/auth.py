from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.limiter import limiter
from app.core.logging import logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ApiResponse,
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & Authorization"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Validates username, email, and password complexity before hashing and saving account.",
)
@limiter.limit("15/minute")
async def register(

    request: Request,
    register_data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[UserResponse]:
    """Register a new user account with secure bcrypt password hashing."""
    user = await auth_service.register_user(db, register_data)
    try:
        import asyncio
        from app.core.audit import extract_client_info, log_audit_background
        ip, ua = extract_client_info(request)
        asyncio.create_task(
            log_audit_background(
                action="user.registered",
                resource="user",
                user_id=user.id,
                resource_id=str(user.id),
                ip_address=ip,
                user_agent=ua,
                status="success",
            )
        )
    except Exception:
        pass

    return ApiResponse(
        success=True,
        message="User account registered successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="OAuth2 Form & JSON Login",
    description="Authenticate using username or email + password. Compatible with Swagger Authorize and JSON clients.",
)
@limiter.limit("30/minute")
async def login(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """OAuth2 password flow and JSON login endpoint returning JWT access and refresh tokens."""
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                username = body.get("username_or_email") or body.get("username")
                password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Malformed JSON body.",
            )
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("username_or_email")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing required credentials (username/email and password).",
        )

    user = await auth_service.authenticate_user(
        db,
        username_or_email=username,
        password=password,
    )
    try:
        import asyncio
        from app.core.audit import extract_client_info, log_audit_background
        ip, ua = extract_client_info(request)
        asyncio.create_task(
            log_audit_background(
                action="user.login",
                resource="user",
                user_id=user.id,
                resource_id=str(user.id),
                ip_address=ip,
                user_agent=ua,
                status="success",
            )
        )
    except Exception:
        pass
    return auth_service.generate_tokens(user)


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="JSON Payload Login",
    description="Authenticate using standard JSON request body with username_or_email and password.",
)
@limiter.limit("30/minute")
async def login_json(

    request: Request,
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Alternative JSON login for SPAs and frontend mobile clients."""
    user = await auth_service.authenticate_user(
        db,
        username_or_email=credentials.username_or_email,
        password=credentials.password,
    )
    try:
        import asyncio
        from app.core.audit import extract_client_info, log_audit_background
        ip, ua = extract_client_info(request)
        asyncio.create_task(
            log_audit_background(
                action="user.login",
                resource="user",
                user_id=user.id,
                resource_id=str(user.id),
                ip_address=ip,
                user_agent=ua,
                status="success",
            )
        )
    except Exception:
        pass
    return auth_service.generate_tokens(user)



@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="Submits a valid refresh token to obtain a brand new access and refresh token pair.",
)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Issue fresh access token using an unexpired refresh token."""
    return await auth_service.refresh_access_token(db, refresh_data.refresh_token)


@router.post(
    "/change-password",
    response_model=ApiResponse[None],
    summary="Change Account Password",
    description="Allows authenticated users to change their password after validating existing credentials.",
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[None]:
    """Change password for currently authenticated user."""
    await auth_service.change_password(db, current_user, password_data)
    return ApiResponse(
        success=True,
        message="Password updated successfully. Please use your new password on subsequent logins.",
        data=None,
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Get Authenticated User Profile",
    description="Fetches current user information parsed from the validated JWT token.",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ApiResponse[UserResponse]:
    """Return account details for the authenticated subject."""
    return ApiResponse(
        success=True,
        message="Current user profile retrieved successfully.",
        data=UserResponse.model_validate(current_user),
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="Log Out User",
    description="Terminates active session (placeholder for distributed token invalidation/blacklist).",
)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ApiResponse[None]:
    """Logout authenticated user session."""
    await auth_service.logout_user(current_user)
    return ApiResponse(
        success=True,
        message="Successfully logged out of active session.",
        data=None,
    )
