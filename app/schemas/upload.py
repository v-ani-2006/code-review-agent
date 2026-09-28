from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.history import HistoryItem


class UploadMetadata(BaseModel):
    """Metadata detailing an uploaded source code file or archive."""

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    stored_filename: str
    file_size: int
    file_hash: str
    mime_type: str
    language: str
    uploaded_at: datetime
    review_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """Response payload returned upon successfully uploading and reviewing a file."""

    success: bool = True
    message: str
    upload: UploadMetadata
    review: Optional[HistoryItem] = None
    reused_existing_review: bool = False


class MultipleUploadResponse(BaseModel):
    """Aggregated response returned when uploading multiple files concurrently."""

    success: bool = True
    total_files: int
    successful_files: int
    failed_files: int
    results: List[UploadResponse] = Field(default_factory=list)


class FilePreviewResponse(BaseModel):
    """Head preview of an uploaded file."""

    upload_id: uuid.UUID
    filename: str
    language: str
    total_lines: int
    preview_lines: List[str]
    truncated: bool = False
