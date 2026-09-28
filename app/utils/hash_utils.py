import hashlib
from pathlib import Path
from typing import Union


def calculate_sha256(data: bytes) -> str:
    """Compute hex SHA-256 digest of raw byte content."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def calculate_file_sha256(filepath: Union[str, Path], chunk_size: int = 65536) -> str:
    """Stream and compute hex SHA-256 digest of a local filesystem file."""
    hasher = hashlib.sha256()
    path = Path(filepath)
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def calculate_string_sha256(text: str) -> str:
    """Compute hex SHA-256 digest of a UTF-8 string."""
    return calculate_sha256(text.encode("utf-8"))
