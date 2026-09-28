import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyzer import analyze_code
from app.core.logging import logger
from app.models.upload import Upload
from app.models.user import User
from app.repositories.history_repository import history_repository
from app.repositories.review_repository import review_repository
from app.repositories.upload_repository import upload_repository
from app.schemas.history import HistoryItem
from app.schemas.upload import (
    FilePreviewResponse,
    MultipleUploadResponse,
    UploadMetadata,
    UploadResponse,
)
from app.utils.file_utils import (
    async_read_bytes,
    async_write_bytes,
    decode_file_content,
    get_file_preview,
    sanitize_filename,
    validate_code_file,
)
from app.utils.hash_utils import calculate_sha256
from app.utils.language_detector import detect_language_from_filename


UPLOAD_STORAGE_DIR = Path("app/uploads/temp")


class UploadService:
    """Service handling file uploads, validation, deduplication hashing, and automatic review triggering."""

    def __init__(self):
        UPLOAD_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    async def upload_and_analyze_file(
        self,
        db: AsyncSession,
        user: User,
        file: UploadFile,
    ) -> UploadResponse:
        """Validate, store, hash, and review an uploaded source code file."""
        raw_bytes = await file.read()
        filename = sanitize_filename(file.filename or "uploaded_file.py")

        # 1. Validation
        is_valid, error_msg = validate_code_file(filename=filename, content=raw_bytes)
        if not is_valid:
            logger.warning("Upload validation failed for %s: %s", filename, error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        # 2. Compute SHA-256 hash for deduplication
        file_hash = calculate_sha256(raw_bytes)
        existing_upload = await upload_repository.get_by_hash(db, user_id=user.id, file_hash=file_hash)

        # Check if identical review can be reused
        if existing_upload and existing_upload.review_id:
            reused_review = await history_repository.get_review_by_id(
                db,
                review_id=existing_upload.review_id,
                user_id=user.id,
                is_admin=user.is_admin,
            )
            if reused_review:
                logger.info(
                    "Reusing existing review %s for duplicate file hash %s (user %s)",
                    existing_upload.review_id,
                    file_hash[:8],
                    user.username,
                )
                return UploadResponse(
                    success=True,
                    message=f"Identical file '{filename}' was previously analyzed. Reused existing review.",
                    upload=UploadMetadata.model_validate(existing_upload),
                    review=HistoryItem.model_validate(reused_review),
                    reused_existing_review=True,
                )

        # 3. Store file to disk safely
        stored_name = f"{uuid.uuid4()}_{filename}"
        stored_path = UPLOAD_STORAGE_DIR / stored_name
        await async_write_bytes(stored_path, raw_bytes)

        # 4. Decode content and run AST analysis
        source_code = decode_file_content(raw_bytes)
        language = detect_language_from_filename(filename) or "python"

        start_time = time.perf_counter()
        report = analyze_code(code=source_code, filename=filename, language=language)
        duration = round(time.perf_counter() - start_time, 4)

        # 5. Persist Review record
        created_review = await review_repository.create_review(
            db=db,
            user_id=user.id,
            language=language,
            filename=filename,
            source_code=source_code,
            summary=report.summary,
            readability_score=report.scores.readability,
            security_score=report.scores.security,
            complexity_score=report.scores.complexity,
            maintainability_score=report.scores.maintainability,
            overall_score=report.scores.overall,
            favorite=False,
        )
        created_review.analysis_duration = duration
        await db.commit()
        await db.refresh(created_review)

        # 6. Persist Upload metadata
        upload_record = await upload_repository.create_upload(
            db=db,
            user_id=user.id,
            original_filename=filename,
            stored_filename=stored_name,
            file_size=len(raw_bytes),
            file_hash=file_hash,
            mime_type=file.content_type or "text/x-python",
            language=language,
            review_id=created_review.id,
        )

        logger.info(
            "File uploaded and analyzed: upload_id=%s review_id=%s filename='%s' user=%s",
            upload_record.id,
            created_review.id,
            filename,
            user.username,
        )

        try:
            import asyncio
            from app.core.audit import log_audit_background
            from app.core.metrics import metrics_collector
            from app.services.webhook_service import webhook_service

            metrics_collector.record_upload(language, status="success")
            asyncio.create_task(
                webhook_service.broadcast_event_background(
                    event_type="upload.completed",
                    payload_data={
                        "upload_id": str(upload_record.id),
                        "filename": filename,
                        "file_size": upload_record.file_size,
                        "user_id": str(user.id),
                    },
                )
            )
            asyncio.create_task(
                log_audit_background(
                    action="file.uploaded",
                    resource="upload",
                    user_id=user.id,
                    resource_id=str(upload_record.id),
                    status="success",
                    metadata={"filename": filename, "file_size": upload_record.file_size},
                )
            )
        except Exception:
            pass

        return UploadResponse(

            success=True,
            message=f"File '{filename}' successfully uploaded and analyzed.",
            upload=UploadMetadata.model_validate(upload_record),
            review=HistoryItem.model_validate(created_review),
            reused_existing_review=False,
        )

    async def upload_multiple_files(
        self,
        db: AsyncSession,
        user: User,
        files: List[UploadFile],
    ) -> MultipleUploadResponse:
        """Upload and analyze multiple files sequentially or concurrently."""
        results: List[UploadResponse] = []
        successful = 0
        failed = 0

        for file in files:
            try:
                res = await self.upload_and_analyze_file(db, user, file)
                results.append(res)
                successful += 1
            except Exception as exc:
                failed += 1
                logger.error("Failed uploading file %s: %s", file.filename, str(exc))

        return MultipleUploadResponse(
            success=successful > 0,
            total_files=len(files),
            successful_files=successful,
            failed_files=failed,
            results=results,
        )

    async def get_preview(
        self,
        db: AsyncSession,
        user: User,
        upload_id: uuid.UUID,
        max_lines: int = 50,
    ) -> FilePreviewResponse:
        """Fetch head preview of an uploaded file."""
        upload = await upload_repository.get_upload_by_id(db, upload_id=upload_id, user_id=user.id, is_admin=user.is_admin)
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload '{upload_id}' not found.",
            )

        stored_file_path = UPLOAD_STORAGE_DIR / upload.stored_filename
        if not stored_file_path.exists():
            # If temp file removed, fetch from Review model if exists
            if upload.review:
                content = upload.review.source_code
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Underlying stored file has been purged from temporary storage.",
                )
        else:
            content_bytes = await async_read_bytes(stored_file_path)
            content = decode_file_content(content_bytes)

        preview_lines, total_lines = get_file_preview(content, max_lines=max_lines)

        return FilePreviewResponse(
            upload_id=upload.id,
            filename=upload.original_filename,
            language=upload.language,
            total_lines=total_lines,
            preview_lines=preview_lines,
            truncated=total_lines > max_lines,
        )

    async def delete_upload(
        self,
        db: AsyncSession,
        user: User,
        upload_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Delete upload metadata and clean up stored file."""
        upload = await upload_repository.get_upload_by_id(db, upload_id=upload_id, user_id=user.id, is_admin=user.is_admin)
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload '{upload_id}' not found.",
            )

        # Delete physical file
        stored_file = UPLOAD_STORAGE_DIR / upload.stored_filename
        if stored_file.exists():
            try:
                stored_file.unlink()
            except Exception:
                pass

        await upload_repository.delete(db, upload.id)
        logger.info("Upload %s deleted by user %s", upload_id, user.username)
        return {
            "success": True,
            "message": f"Upload '{upload_id}' successfully removed.",
        }


upload_service = UploadService()
