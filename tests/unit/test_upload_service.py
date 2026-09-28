"""Unit tests for file upload validation, hashing, sanitization, and upload service."""
import io
import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.upload_service import upload_service
from app.utils.file_utils import (
    get_file_preview,
    sanitize_filename,
    validate_code_file,
)
from app.utils.hash_utils import calculate_sha256


@pytest.mark.unit
def test_sanitize_filename_path_traversal():
    """Test that path traversal attempts are stripped from filename."""
    dangerous_filename = "../../../etc/passwd"
    sanitized = sanitize_filename(dangerous_filename)
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert ".." not in sanitized


@pytest.mark.unit
def test_validate_code_file_valid():
    """Test validation on standard valid Python source file."""
    content = b"def greet():\n    return 'Hello'\n"
    is_valid, err = validate_code_file("greet.py", content)
    assert is_valid is True
    assert err is None


@pytest.mark.unit
def test_validate_code_file_unsupported_extension():
    """Test rejection of unsupported file extensions (e.g. .exe, .bin)."""
    content = b"Binary machine code"
    is_valid, err = validate_code_file("malicious.exe", content)
    assert is_valid is False
    assert "unsupported" in err.lower() or "extension" in err.lower()


@pytest.mark.unit
def test_validate_code_file_oversized():
    """Test rejection when file exceeds maximum allowed bytes (25MB limit)."""
    # 30MB exceeds the 25MB MAX_UPLOAD_SIZE_BYTES limit
    oversized_content = b"A" * (30 * 1024 * 1024)
    is_valid, err = validate_code_file("large.py", oversized_content)
    assert is_valid is False
    assert "size" in err.lower() or "limit" in err.lower() or "exceed" in err.lower()


@pytest.mark.unit
def test_calculate_sha256_deterministic():
    """Test SHA256 checksum calculation reproducibility."""
    payload = b"deterministic python source code content"
    hash1 = calculate_sha256(payload)
    hash2 = calculate_sha256(payload)
    assert hash1 == hash2
    assert len(hash1) == 64


@pytest.mark.unit
def test_get_file_preview():
    """Test file preview line clipping."""
    multiline = "line1\nline2\nline3\nline4\nline5\nline6"
    preview_lines, total = get_file_preview(multiline, max_lines=3)
    assert len(preview_lines) <= 3
    assert total == 6


@pytest.mark.unit
async def test_upload_and_analyze_service(db_session: AsyncSession, test_user: User):
    """Test upload_and_analyze_file processing."""
    file_bytes = b"def compute():\n    return 42\n"
    upload_file = UploadFile(
        file=io.BytesIO(file_bytes),
        filename="compute.py",
        headers={"content-type": "text/x-python"},
    )

    res = await upload_service.upload_and_analyze_file(db_session, test_user, upload_file)
    assert res is not None
    assert res.upload.original_filename == "compute.py"
    assert res.review is not None
    assert res.review.overall_score > 0
