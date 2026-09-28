import uuid
from typing import Annotated, Callable, List, Optional
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import oauth2_scheme, verify_token
from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.api_key import APIKey
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.services.api_key_service import api_key_service

# Optional OAuth2 scheme that does not raise 401 when token is missing
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)

api_key_header_scheme = APIKeyHeader(
    name=settings.API_KEY_HEADER,
    auto_error=False,
)


async def get_optional_user(
    request: Request,
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)],
    api_key_val: Annotated[Optional[str], Depends(api_key_header_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """Retrieve authenticated user via Bearer JWT or API Key; returns None if neither provided."""
    # 1. Try Bearer JWT
    if token:
        try:
            payload = verify_token(token, expected_type="access")
            user_id_str = payload.get("sub") or payload.get("user_id")
            user_uuid = uuid.UUID(user_id_str)
            return await user_repository.get_by_id(db, user_uuid)
        except Exception:
            pass

    # 2. Try API Key Header
    if api_key_val:
        try:
            auth_res = await api_key_service.authenticate_api_key(db, api_key_val)
            if auth_res:
                user, key_obj = auth_res
                request.state.api_key = key_obj
                return user
        except Exception:
            pass

    return None


async def get_current_user(
    request: Request,
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)],
    api_key_val: Annotated[Optional[str], Depends(api_key_header_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Validate Bearer JWT or X-API-Key header and return authenticated User record."""
    # 1. Bearer JWT
    if token:
        try:
            payload = verify_token(token, expected_type="access")
            user_id_str = payload.get("sub") or payload.get("user_id")
            user_uuid = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            logger.warning("Authentication failed: Malformed UUID in token subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token claims.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(exc)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await user_repository.get_by_id(db, user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    # 2. API Key Header
    if api_key_val:
        auth_res = await api_key_service.authenticate_api_key(db, api_key_val)
        if not auth_res:
            logger.warning("Authentication failed: Invalid or expired API Key '%s'", api_key_val[:8])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API Key.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        user, key_obj = auth_res
        request.state.api_key = key_obj
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )


get_current_user_or_api_key = get_current_user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Enforce that the authenticated user account is active."""
    if not current_user.is_active:
        logger.warning("Unauthorized access: User account '%s' is deactivated", current_user.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Please contact support.",
        )
    return current_user


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Enforce role-based authorization: require administrative privileges."""
    if not current_user.is_admin:
        logger.warning(
            "Unauthorized admin access attempt: User '%s' lacking admin privileges",
            current_user.username,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource.",
        )
    return current_user


def require_permission(required_scope: str):
    """Enforce fine-grained API Key permissions if request was authenticated via API key."""
    async def _check_scope(
        request: Request,
        user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        key_obj: Optional[APIKey] = getattr(request.state, "api_key", None)
        if key_obj:
            perms = key_obj.permissions or []
            if "*" not in perms and required_scope not in perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API Key does not possess the required permission scope: '{required_scope}'.",
                )
        return user

    return _check_scope
