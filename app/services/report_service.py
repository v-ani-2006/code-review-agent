from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Tuple

import uuid
import zipfile
from fastapi import HTTPException, status

from app.ai.export_service import export_engine
from app.core.logging import logger
from app.schemas.batch import BatchReviewResponse
from app.schemas.report import ReportListResponse, ReportMetadata, ReportResponse
from app.utils.file_utils import async_read_text, async_write_text


REPORTS_DIR = Path("app/uploads/reports")


class ReportService:
    """Service generating, archiving, and serving multi-format project review reports."""

    def __init__(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    async def generate_and_save_report(
        self,
        batch_review: BatchReviewResponse,
        project_name: str = "project",
    ) -> str:
        """Create JSON, Markdown, HTML, and ZIP audit packages on disk and return report_id."""
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        report_folder = REPORTS_DIR / report_id
        report_folder.mkdir(parents=True, exist_ok=True)

        payload_dict = batch_review.model_dump(mode="json")
        payload_dict["project_name"] = project_name
        payload_dict["created_at"] = datetime.now(timezone.utc).isoformat()

        # 1. JSON Report
        json_path = report_folder / f"{project_name}_report.json"
        await async_write_text(json_path, json.dumps(payload_dict, indent=2))

        # 2. Markdown Report
        md_content = self._render_markdown_report(batch_review, project_name)
        md_path = report_folder / f"{project_name}_report.md"
        await async_write_text(md_path, md_content)

        # 3. HTML Report
        html_content = export_engine.to_html(md_content, title=f"CodePilot Project Audit — {project_name}")
        html_path = report_folder / f"{project_name}_report.html"
        await async_write_text(html_path, html_content)

        # 4. Compressed ZIP archive containing all three formats
        zip_path = report_folder / f"{project_name}_audit_package.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(json_path, arcname=json_path.name)
            zf.write(md_path, arcname=md_path.name)
            zf.write(html_path, arcname=html_path.name)

        logger.info("Report %s generated successfully for %s at %s", report_id, project_name, report_folder)
        return report_id

    def _render_markdown_report(
        self,
        batch: BatchReviewResponse,
        project_name: str,
    ) -> str:
        """Render a clean GitHub-flavored markdown report summarizing project analysis."""
        lines = [
            f"# CodePilot AI Project Code Review: `{project_name}`",
            "",
            f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"> **Overall Project Score:** `{batch.overall_project_score}/100`  ",
            f"> **Total Analyzed Files:** `{batch.total_files_analyzed}`",
            "",
            "## 1. Executive Summary",
            f"- **Security Summary:** {batch.security_summary}",
            f"- **Complexity Summary:** {batch.complexity_summary}",
            f"- **Documentation:** {batch.documentation_summary}",
            f"- **Critical Issues Logged:** `{batch.critical_issues}`",
            f"- **Total Issues Identified:** `{batch.total_issues}`",
            "",
            "## 2. Project Architecture & Metrics",
            f"- **Total Source Lines:** `{batch.project_metrics.total_lines}`",
            f"- **Functions Defined:** `{batch.project_metrics.total_functions}`",
            f"- **Classes Declared:** `{batch.project_metrics.total_classes}`",
            f"- **Average Maintainability Index:** `{batch.average_maintainability}/100`",
            f"- **Average Readability Score:** `{batch.average_readability}/100`",
            f"- **Duplicate Imports Detected:** `{batch.project_metrics.duplicate_imports_count}`",
            "",
        ]

        if batch.directory_tree:
            lines.extend([
                "## 3. Directory Structure Tree",
                "```text",
                batch.directory_tree,
                "```",
                "",
            ])

        lines.extend([
            "## 4. File-by-File Breakdown",
            "| Filename | Score | Security | Complexity | Readability |",
            "|---|---|---|---|---|",
        ])

        for rev in batch.file_reviews:
            lines.append(
                f"| `{rev.filename}` | {rev.overall_score or 'N/A'} | {rev.security_score or 'N/A'} | {rev.complexity_score or 'N/A'} | {rev.readability_score or 'N/A'} |"
            )

        lines.extend([
            "",
            "---",
            "*Report compiled automatically by CodePilot AI Project Review Engine.*",
        ])
        return "\n".join(lines)

    async def get_report(self, report_id: str) -> ReportResponse:
        """Fetch metadata and download paths for a saved report."""
        report_dir = REPORTS_DIR / report_id
        if not report_dir.exists() or not report_dir.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report '{report_id}' was not found.",
            )

        json_files = list(report_dir.glob("*.json"))
        if not json_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report manifest missing.",
            )

        manifest_text = await async_read_text(json_files[0])
        data = json.loads(manifest_text)

        formats = {
            "json": f"/reports/{report_id}/download?format=json",
            "markdown": f"/reports/{report_id}/download?format=markdown",
            "html": f"/reports/{report_id}/download?format=html",
            "zip": f"/reports/{report_id}/download?format=zip",
        }

        return ReportResponse(
            success=True,
            report_id=report_id,
            project_name=data.get("project_name", "Project"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            overall_score=data.get("overall_project_score", 0.0),
            total_files=data.get("total_files_analyzed", 0),
            formats=formats,
            summary_data=data,
        )

    async def get_report_file(
        self,
        report_id: str,
        export_format: str = "json",
    ) -> Tuple[Path, str, str]:
        """Resolve file path, mime-type, and filename for report download."""
        report_dir = REPORTS_DIR / report_id
        if not report_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report '{report_id}' not found.",
            )

        fmt = export_format.lower().strip()
        if fmt == "markdown":
            matches = list(report_dir.glob("*.md"))
            mime = "text/markdown"
        elif fmt == "html":
            matches = list(report_dir.glob("*.html"))
            mime = "text/html"
        elif fmt == "zip":
            matches = list(report_dir.glob("*.zip"))
            mime = "application/zip"
        else:
            matches = list(report_dir.glob("*.json"))
            mime = "application/json"

        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report format '{fmt}' not available for report '{report_id}'.",
            )

        file_path = matches[0]
        return file_path, mime, file_path.name

    async def list_reports(self) -> ReportListResponse:
        """List all generated project reports available on disk."""
        reports: List[ReportMetadata] = []
        for d in REPORTS_DIR.iterdir():
            if d.is_dir() and d.name.startswith("report_"):
                json_files = list(d.glob("*.json"))
                if json_files:
                    try:
                        with open(json_files[0], "r", encoding="utf-8") as f:
                            data = json.load(f)
                        reports.append(
                            ReportMetadata(
                                report_id=d.name,
                                project_name=data.get("project_name", "Project"),
                                created_at=datetime.fromisoformat(
                                    data.get("created_at", datetime.now(timezone.utc).isoformat())
                                ),
                                overall_score=data.get("overall_project_score", 0.0),
                                total_files=data.get("total_files_analyzed", 0),
                            )
                        )
                    except Exception:
                        continue

        # Sort by creation time desc
        reports.sort(key=lambda r: r.created_at, reverse=True)
        return ReportListResponse(success=True, total_reports=len(reports), reports=reports)

    async def delete_report(self, report_id: str) -> Dict[str, Any]:
        """Remove saved report directory and artifacts from disk."""
        report_dir = REPORTS_DIR / report_id
        if not report_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report '{report_id}' not found.",
            )
        shutil.rmtree(report_dir, ignore_errors=True)
        logger.info("Report %s purged from storage", report_id)
        return {"success": True, "message": f"Report '{report_id}' successfully deleted."}


report_service = ReportService()
