from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import VersionResponse

# APIRouter instance for version and environment diagnostics
router = APIRouter(tags=["System Info"])


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Application Version & Configuration",
    description="Returns version metadata, active API routing prefix, and debug status.",
)
async def get_version() -> VersionResponse:
    """Return runtime metadata and active configuration details."""
    return VersionResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        api_prefix=settings.API_PREFIX,
        debug=settings.DEBUG,
        build_commit=settings.BUILD_COMMIT,
        build_timestamp=settings.BUILD_TIMESTAMP,
    )
