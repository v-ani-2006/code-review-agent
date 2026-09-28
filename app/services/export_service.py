import time
from typing import Any, Dict, Optional

from app.ai.export_service import export_engine
from app.core.logging import logger
from app.schemas.exports import ExportRequest, ExportResponse


class ExportService:
    """Service providing document formatting and multi-format exports."""

    def export_json(self, request: ExportRequest) -> ExportResponse:
        """Export payload as JSON."""
        start_time = time.perf_counter()
        data = request.data if request.data is not None else {"content": request.content}
        serialized = export_engine.to_json(data, pretty=request.pretty)
        duration = round(time.perf_counter() - start_time, 4)
        base_name = request.filename or "report"
        return ExportResponse(
            success=True,
            format="json",
            filename=f"{base_name}.json",
            mime_type="application/json",
            content=serialized,
            processing_time=duration,
        )

    def export_markdown(self, request: ExportRequest) -> ExportResponse:
        """Export payload as Markdown."""
        start_time = time.perf_counter()
        if request.content:
            md_content = request.content
        elif request.data:
            md_content = export_engine.to_markdown(request.data)
        else:
            md_content = "# Empty Report\n\nNo content provided for export."

        duration = round(time.perf_counter() - start_time, 4)
        base_name = request.filename or "report"
        return ExportResponse(
            success=True,
            format="markdown",
            filename=f"{base_name}.md",
            mime_type="text/markdown",
            content=md_content,
            processing_time=duration,
        )

    def export_html(self, request: ExportRequest) -> ExportResponse:
        """Export payload as standalone responsive HTML."""
        start_time = time.perf_counter()
        if request.content:
            md_content = request.content
        elif request.data:
            md_content = export_engine.to_markdown(request.data)
        else:
            md_content = "# Empty Report\n\nNo content provided for export."

        html_content = export_engine.to_html(md_content, title=request.title or "CodePilot AI Report")
        duration = round(time.perf_counter() - start_time, 4)
        base_name = request.filename or "report"
        return ExportResponse(
            success=True,
            format="html",
            filename=f"{base_name}.html",
            mime_type="text/html",
            content=html_content,
            processing_time=duration,
        )

    def export_text(self, request: ExportRequest) -> ExportResponse:
        """Export payload as plain text."""
        start_time = time.perf_counter()
        if request.content:
            text_content = export_engine.to_plain_text(request.content)
        elif request.data:
            md_temp = export_engine.to_markdown(request.data)
            text_content = export_engine.to_plain_text(md_temp)
        else:
            text_content = "Empty Report\nNo content provided for export."

        duration = round(time.perf_counter() - start_time, 4)
        base_name = request.filename or "report"
        return ExportResponse(
            success=True,
            format="text",
            filename=f"{base_name}.txt",
            mime_type="text/plain",
            content=text_content,
            processing_time=duration,
        )


# Singleton export service
app_export_service = ExportService()
