"""Sample test files and zip archive helpers."""
from pathlib import Path
from tests.sample_files.generate_zip_samples import build_large_project, build_sample_project

SAMPLE_FILES_DIR = Path(__file__).resolve().parent

CLEAN_CODE_PATH = SAMPLE_FILES_DIR / "clean_code.py"
VULNERABLE_CODE_PATH = SAMPLE_FILES_DIR / "vulnerable_code.py"
COMPLEX_CODE_PATH = SAMPLE_FILES_DIR / "complex_code.py"
SYNTAX_ERROR_PATH = SAMPLE_FILES_DIR / "syntax_error.py"
PROJECT_SAMPLE_ZIP_PATH = SAMPLE_FILES_DIR / "project_sample.zip"
LARGE_PROJECT_ZIP_PATH = SAMPLE_FILES_DIR / "large_project.zip"

# Ensure zip artifacts exist
if not PROJECT_SAMPLE_ZIP_PATH.exists():
    build_sample_project()

if not LARGE_PROJECT_ZIP_PATH.exists():
    build_large_project()

__all__ = [
    "SAMPLE_FILES_DIR",
    "CLEAN_CODE_PATH",
    "VULNERABLE_CODE_PATH",
    "COMPLEX_CODE_PATH",
    "SYNTAX_ERROR_PATH",
    "PROJECT_SAMPLE_ZIP_PATH",
    "LARGE_PROJECT_ZIP_PATH",
]
