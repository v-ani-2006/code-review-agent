import os
from pathlib import Path
import re
from typing import List, Optional, Tuple

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB default limit
ALLOWED_EXTENSIONS = {".py", ".pyw"}


def sanitize_filename(filename: str) -> str:
    """Strip path traversal components and unsafe characters from filenames."""
    # Remove directory separators
    clean = os.path.basename(filename)
    # Strip dangerous characters
    clean = re.sub(r"[^\w\.\-\+]", "_", clean)
    return clean or "uploaded_file.py"


def is_binary_content(data: bytes) -> bool:
    """Heuristic check to determine if byte content is compiled/binary rather than text."""
    # Check for null byte
    if b"\x00" in data[:1024]:
        return True
    return False


def decode_file_content(data: bytes) -> str:
    """Decode raw bytes into a UTF-8 string with graceful encoding fallback."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("latin-1")
        except Exception:
            return data.decode("utf-8", errors="replace")


def validate_code_file(
    filename: str,
    content: bytes,
    max_size: int = MAX_UPLOAD_SIZE_BYTES,
) -> Tuple[bool, Optional[str]]:
    """Validate file extension, size, non-emptiness, and text encoding."""
    if len(content) == 0:
        return False, f"File '{filename}' is empty."

    if len(content) > max_size:
        return False, f"File '{filename}' exceeds maximum allowed size ({max_size // (1024 * 1024)}MB)."

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{suffix}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    if is_binary_content(content):
        return False, f"File '{filename}' contains binary data. Plain text source code is required."

    return True, None


def get_file_preview(
    content: str,
    max_lines: int = 50,
) -> Tuple[List[str], int]:
    """Extract first N lines of source code and total line count for preview."""
    lines = content.splitlines()
    total_lines = len(lines)
    preview_lines = lines[:max_lines]
    return preview_lines, total_lines


import asyncio


async def async_write_bytes(path: Path, data: bytes) -> None:
    """Asynchronously write bytes to disk without blocking event loop."""
    await asyncio.to_thread(path.write_bytes, data)


async def async_read_bytes(path: Path) -> bytes:
    """Asynchronously read bytes from disk."""
    return await asyncio.to_thread(path.read_bytes)


async def async_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Asynchronously write string to file."""
    def _write():
        path.write_text(text, encoding=encoding)
    await asyncio.to_thread(_write)


async def async_read_text(path: Path, encoding: str = "utf-8") -> str:
    """Asynchronously read string from file."""
    return await asyncio.to_thread(path.read_text, encoding=encoding, errors="replace")

