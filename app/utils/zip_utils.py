import os
from pathlib import Path
import shutil
from typing import List, Optional, Set, Tuple
import zipfile



MAX_UNCOMPRESSED_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_ZIP_FILES = 500
MAX_COMPRESSION_RATIO = 100

DEFAULT_IGNORED_DIRS: Set[str] = {
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "eggs",
    ".eggs",
}


def validate_and_extract_zip(
    zip_path: Path,
    target_extract_dir: Path,
    max_uncompressed_bytes: int = MAX_UNCOMPRESSED_SIZE_BYTES,
    max_files: int = MAX_ZIP_FILES,
) -> Tuple[bool, Optional[str], List[Path]]:
    """Safely validate and extract a ZIP archive protecting against ZIP bombs and path traversal."""
    if not zipfile.is_zipfile(zip_path):
        return False, "Uploaded file is not a valid or readable ZIP archive.", []

    target_extract_dir.mkdir(parents=True, exist_ok=True)
    target_abs = target_extract_dir.resolve()

    extracted_files: List[Path] = []
    total_uncompressed = 0
    compressed_size = zip_path.stat().st_size or 1

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            infolist = zf.infolist()

            if len(infolist) > max_files:
                return (
                    False,
                    f"ZIP archive contains too many files ({len(infolist)} > {max_files}).",
                    [],
                )

            for member in infolist:
                # 1. Path traversal check (ZipSlip)
                member_path = Path(member.filename)
                destination = (target_extract_dir / member_path).resolve()
                if not str(destination).startswith(str(target_abs)):
                    return (
                        False,
                        f"Malicious archive member detected (ZipSlip path traversal attempt): '{member.filename}'",
                        [],
                    )

                # 2. Cumulative uncompressed size check (ZipBomb protection)
                total_uncompressed += member.file_size
                if total_uncompressed > max_uncompressed_bytes:
                    return (
                        False,
                        f"Decompressed archive exceeds size limit ({max_uncompressed_bytes // (1024 * 1024)}MB).",
                        [],
                    )

                # 3. Compression ratio check
                ratio = member.file_size / max(member.compress_size, 1)
                if ratio > MAX_COMPRESSION_RATIO and member.file_size > 1024 * 1024:
                    return (
                        False,
                        f"Suspicious compression ratio detected in file '{member.filename}'.",
                        [],
                    )

            # Safe to extract
            for member in infolist:
                if member.is_dir():
                    continue

                dest_file = target_extract_dir / member.filename
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                with zf.open(member) as source, open(dest_file, "wb") as target:
                    shutil.copyfileobj(source, target)

                extracted_files.append(dest_file)

        return True, None, extracted_files

    except Exception as exc:
        return False, f"Failed to safely extract ZIP archive: {str(exc)}", []


def generate_directory_tree(
    root_dir: Path,
    ignore_dirs: Set[str] = DEFAULT_IGNORED_DIRS,
    max_depth: int = 5,
) -> str:
    """Generate an ASCII directory tree representation of the extracted project."""
    tree_lines: List[str] = [root_dir.name + "/"]

    def _build_tree(directory: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except Exception:
            return

        # Filter ignored
        filtered_entries = [
            e for e in entries if e.name not in ignore_dirs and not e.name.startswith(".")
        ]

        count = len(filtered_entries)
        for idx, entry in enumerate(filtered_entries):
            is_last = idx == (count - 1)
            connector = "└── " if is_last else "├── "
            sub_prefix = "    " if is_last else "│   "

            if entry.is_dir():
                tree_lines.append(f"{prefix}{connector}{entry.name}/")
                _build_tree(entry, prefix + sub_prefix, depth + 1)
            else:
                tree_lines.append(f"{prefix}{connector}{entry.name}")

    _build_tree(root_dir)
    return "\n".join(tree_lines)


def cleanup_directory(path: Path) -> bool:
    """Recursively remove a directory and its contents safely."""
    try:
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            return True
        elif path.exists() and path.is_file():
            path.unlink()
            return True
        return False
    except Exception:
        return False
