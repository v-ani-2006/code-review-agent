from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.limiter import limiter
from app.db.session import get_db

from app.models.user import User
from app.repositories.task_repository import task_repository
from app.repositories.upload_repository import upload_repository
from app.schemas.batch import BatchReviewResponse
from app.schemas.upload import (
    FilePreviewResponse,
    MultipleUploadResponse,
    UploadMetadata,
    UploadResponse,
)
from app.services.batch_service import batch_service
from app.services.upload_service import upload_service
from app.utils.file_utils import async_write_bytes, sanitize_filename


router = APIRouter(prefix="/upload", tags=["Uploads"])
TEMP_DIR = Path("app/uploads/temp")


@router.post(
    "/file",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Review Single File",
    description="Upload a Python source code file (.py). Performs validation, SHA-256 deduplication, static analysis, and review persistence.",
)
@limiter.limit("30/minute")
async def upload_single_file(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(..., description="Python source code file (.py)"),
) -> UploadResponse:
    """Upload and review a single code file."""
    return await upload_service.upload_and_analyze_file(db=db, user=current_user, file=file)


@router.post(
    "/code-file",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Code File (Alias)",
    description="Alternative endpoint to upload and inspect a single Python file.",
)
@limiter.limit("30/minute")
async def upload_code_file_alias(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(..., description="Python code file"),
) -> UploadResponse:
    """Upload single code file."""
    return await upload_service.upload_and_analyze_file(db=db, user=current_user, file=file)



@router.post(
    "/files",
    response_model=MultipleUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Multiple Files",
    description="Upload multiple Python files simultaneously. Evaluates each file and persists reviews.",
)
@router.post("/multiple", response_model=MultipleUploadResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def upload_multiple_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    files: List[UploadFile] = File(..., description="Multiple Python code files"),
) -> MultipleUploadResponse:
    """Upload multiple source files."""
    return await upload_service.upload_multiple_files(db=db, user=current_user, files=files)


@router.post(
    "/project",
    response_model=BatchReviewResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload ZIP Project Archive",
    description="Upload a ZIP archive containing a Python project repository. Validates for ZipBombs/ZipSlip, extracts safely, scans files recursively, and initiates audit analysis.",
)
@router.post("/zip", response_model=BatchReviewResponse, status_code=status.HTTP_202_ACCEPTED, include_in_schema=False)
async def upload_project_zip(
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(..., description="ZIP project archive (.zip)"),
    project_name: Optional[str] = Query(None, description="Optional project display name"),
    run_in_background: bool = Query(False, description="Process in background task"),
) -> BatchReviewResponse:
    """Upload and inspect a full ZIP project repository."""
    raw_filename = sanitize_filename(file.filename or "project.zip")
    if not raw_filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .zip archive archives are accepted for project scanning.",
        )

    # Save ZIP to temp storage
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_zip_path = TEMP_DIR / f"{uuid.uuid4()}_{raw_filename}"
    zip_bytes = await file.read()
    await async_write_bytes(temp_zip_path, zip_bytes)

    proj_title = project_name or Path(raw_filename).stem

    # Create task record
    task = await task_repository.create_task(
        db,
        user_id=current_user.id,
        task_type="zip_project",
        filename=raw_filename,
    )

    if run_in_background:
        background_tasks.add_task(
            batch_service.run_project_analysis_background,
            user_id=current_user.id,
            zip_file_path=temp_zip_path,
            project_name=proj_title,
            task_id=task.id,
        )
        return BatchReviewResponse(
            task_id=task.id,
            status="PENDING",
            overall_project_score=0.0,
            total_files_analyzed=0,
            total_issues=0,
            critical_issues=0,
            security_summary="Analysis scheduled in background.",
            complexity_summary="Pending background job processing.",
            documentation_summary="Pending background job processing.",
            average_readability=0.0,
            average_maintainability=0.0,
            project_metrics=None,  # type: ignore
        )
    else:
        # Run synchronously
        return await batch_service.execute_project_pipeline(
            db=db,
            user=current_user,
            zip_file_path=temp_zip_path,
            project_name=proj_title,
            task=task,
        )


@router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    summary="List User Uploads",
    description="Retrieve all files uploaded by the current authenticated user.",
)
async def get_user_uploads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Dict[str, Any]]:
    """List current user uploads."""
    items, _ = await upload_repository.search_uploads(db, user_id=current_user.id, page=1, page_size=100)
    return [UploadMetadata.model_validate(u).model_dump(mode="json") for u in items]


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search Uploaded Files",
    description="Search upload records by filename, language, hash, date range, or review ID.",
)
async def search_uploaded_files(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    filename: Optional[str] = Query(None, description="Filename filter"),
    language: Optional[str] = Query(None, description="Language filter"),
    file_hash: Optional[str] = Query(None, description="SHA-256 hash filter"),
    review_id: Optional[uuid.UUID] = Query(None, description="Associated review UUID"),
    date_from: Optional[datetime] = Query(None, description="Uploaded date start"),
    date_to: Optional[datetime] = Query(None, description="Uploaded date end"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Dict[str, Any]:
    """Search uploaded files."""
    items, total = await upload_repository.search_uploads(
        db=db,
        user_id=current_user.id,
        filename=filename,
        language=language,
        file_hash=file_hash,
        review_id=review_id,
        date_from=date_from,
        date_to=date_to,
        is_admin=current_user.is_admin,
        page=page,
        page_size=page_size,
    )
    return {
        "success": True,
        "total_items": total,
        "page": page,
        "page_size": page_size,
        "items": [UploadMetadata.model_validate(u) for u in items],
    }


@router.get(
    "/{upload_id}",
    response_model=UploadMetadata,
    status_code=status.HTTP_200_OK,
    summary="Get Upload Metadata",
    description="Fetch stored metadata for an upload record.",
)
async def get_upload_metadata(
    upload_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UploadMetadata:
    """Fetch upload metadata."""
    upload = await upload_repository.get_upload_by_id(
        db,
        upload_id=upload_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
    )
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' not found.",
        )
    return UploadMetadata.model_validate(upload)


@router.get(
    "/{upload_id}/preview",
    response_model=FilePreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get File Preview",
    description="Fetch the first N lines of source code for an uploaded file.",
)
async def get_uploaded_file_preview(
    upload_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    lines: int = Query(50, ge=1, le=500, description="Max lines to preview"),
) -> FilePreviewResponse:
    """Preview uploaded file contents."""
    return await upload_service.get_preview(db=db, user=current_user, upload_id=upload_id, max_lines=lines)


@router.delete(
    "/{upload_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Upload",
    description="Delete upload record and remove the stored physical file from disk.",
)
async def delete_upload(
    upload_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Delete upload."""
    return await upload_service.delete_upload(db=db, user=current_user, upload_id=upload_id)
