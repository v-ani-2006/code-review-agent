"""Utility script to generate sample project zip files for upload and batch testing."""
import io
from pathlib import Path
import zipfile

SAMPLE_DIR = Path(__file__).resolve().parent

def build_sample_project():
    """Create project_sample.zip containing standard multi-module python repository."""
    zip_path = SAMPLE_DIR / "project_sample.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "src/__init__.py",
            '"""Main package."""\n__version__ = "1.0.0"\n'
        )
        zf.writestr(
            "src/calculator.py",
            '''"""Calculator module."""
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b
'''
        )
        zf.writestr(
            "src/utils.py",
            '''"""Utilities."""
def sanitize_text(text: str) -> str:
    return text.strip().lower()
'''
        )
        zf.writestr(
            "README.md",
            "# Sample Project\nA simple test project for CodePilot batch upload testing.\n"
        )
    return zip_path


def build_large_project():
    """Create large_project.zip containing 12 modules across 3 packages."""
    zip_path = SAMPLE_DIR / "large_project.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.md", "# Large Project Suite\nMulti-module architecture benchmark.\n")
        zf.writestr("package_a/__init__.py", '"""Package A"""\n')
        zf.writestr("package_b/__init__.py", '"""Package B"""\n')
        zf.writestr("package_c/__init__.py", '"""Package C"""\n')

        for pkg in ["package_a", "package_b", "package_c"]:
            for i in range(1, 5):
                code = f'''"""Module {pkg}_{i}."""
from typing import List

def compute_metric_{i}(items: List[int]) -> int:
    """Calculates sum of indexed items."""
    total = 0
    for x in items:
        if x > {i}:
            total += x * {i}
    return total

def format_metric_{i}(val: int) -> str:
    return f"Metric {i}: {{val}}"
'''
                zf.writestr(f"{pkg}/module_{i}.py", code)
    return zip_path


if __name__ == "__main__":
    p1 = build_sample_project()
    p2 = build_large_project()
    print(f"Generated {p1.name} and {p2.name}")
