import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

from app.schemas.batch import ProjectMetricsResponse
from app.utils.zip_utils import DEFAULT_IGNORED_DIRS, generate_directory_tree


class ProjectScanService:
    """Service scanning project directories, detecting Python packages, and computing AST metrics."""

    def scan_directory(
        self,
        root_dir: Path,
        ignored_dirs: Set[str] = DEFAULT_IGNORED_DIRS,
    ) -> Tuple[List[Path], List[str], str]:
        """Recursively scan directory for Python files and packages, excluding ignored directories."""
        python_files: List[Path] = []
        packages: List[str] = []

        for path in root_dir.rglob("*.py"):
            parts = set(path.parts)
            # Check if any parent path is in ignored directories
            if not parts.intersection(ignored_dirs) and not any(p.startswith(".") for p in path.parts if p != "."):
                python_files.append(path)
                if path.name == "__init__.py":
                    packages.append(path.parent.name)

        # Generate directory tree
        tree = generate_directory_tree(root_dir, ignore_dirs=ignored_dirs)

        return sorted(python_files), sorted(list(set(packages))), tree

    def compute_project_ast_metrics(
        self,
        files: List[Path],
    ) -> ProjectMetricsResponse:
        """Parse files via Python AST and compute lines, functions, classes, and duplicate imports."""
        total_lines = 0
        total_functions = 0
        total_classes = 0
        seen_imports: Set[str] = set()
        duplicate_imports_count = 0

        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                total_lines += len(content.splitlines())

                tree = ast.parse(content, filename=f.name)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                    elif isinstance(node, ast.ClassDef):
                        total_classes += 1
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in seen_imports:
                                duplicate_imports_count += 1
                            else:
                                seen_imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            full_name = f"{module}.{alias.name}"
                            if full_name in seen_imports:
                                duplicate_imports_count += 1
                            else:
                                seen_imports.add(full_name)

            except Exception:
                continue

        return ProjectMetricsResponse(
            total_files=len(files),
            total_lines=total_lines,
            total_functions=total_functions,
            total_classes=total_classes,
            average_complexity=0.0,
            average_security_score=0.0,
            average_readability=0.0,
            average_maintainability=0.0,
            duplicate_imports_count=duplicate_imports_count,
            critical_findings_count=0,
        )


project_scan_service = ProjectScanService()
