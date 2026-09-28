import asyncio
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyzer import analyze_code
from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.models.task import Task

from app.models.user import User
from app.repositories.review_repository import review_repository
from app.repositories.task_repository import task_repository
from app.schemas.batch import BatchReviewResponse, ProjectMetricsResponse
from app.schemas.history import HistoryItem
from app.services.project_scan_service import project_scan_service
from app.services.report_service import report_service
from app.utils.file_utils import decode_file_content
from app.utils.zip_utils import cleanup_directory, validate_and_extract_zip

TEMP_ZIP_DIR = Path("app/uploads/temp")
EXTRACTED_DIR = Path("app/uploads/extracted")
CONCURRENCY_LIMIT = 5


class BatchService:
    """Service orchestrating concurrent multi-file reviews and full ZIP project analysis pipelines."""

    def __init__(self):
        TEMP_ZIP_DIR.mkdir(parents=True, exist_ok=True)
        EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    async def execute_project_pipeline(
        self,
        db: AsyncSession,
        user: User,
        zip_file_path: Path,
        project_name: str,
        task: Task,
    ) -> BatchReviewResponse:
        """Core execution pipeline analyzing an entire extracted project archive."""
        start_time = time.perf_counter()
        extract_folder = EXTRACTED_DIR / f"{task.id}_{project_name}"

        await task_repository.mark_running(db, task)

        # 1. Validate and safely extract ZIP archive
        is_valid, err_msg, _ = validate_and_extract_zip(
            zip_path=zip_file_path,
            target_extract_dir=extract_folder,
        )
        if not is_valid:
            await task_repository.mark_failed(db, task, err_msg or "Invalid ZIP file.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

        # 2. Recursively scan directory and extract AST metrics
        python_files, packages, tree = project_scan_service.scan_directory(extract_folder)
        ast_metrics = project_scan_service.compute_project_ast_metrics(python_files)

        if not python_files:
            cleanup_directory(extract_folder)
            err = "No valid Python source code files (.py) found in archive."
            await task_repository.mark_failed(db, task, err)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        await task_repository.update_progress(
            db,
            task,
            processed_files=0,
            failed_files=0,
            total_files=len(python_files),
        )

        # 3. Concurrent analysis with Semaphore and a DB lock to prevent
        # concurrent SQLAlchemy session conflicts.
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        db_lock = asyncio.Lock()  # Serialise all DB writes sharing one session
        reviewed_items: List[HistoryItem] = []
        total_issues = 0
        critical_issues = 0
        sum_overall = 0.0
        sum_security = 0.0
        sum_complexity = 0.0
        sum_readability = 0.0
        sum_maintainability = 0.0
        processed_count = 0
        failed_count = 0

        async def analyze_single_file(file_path: Path):
            nonlocal total_issues, critical_issues, sum_overall, sum_security
            nonlocal sum_complexity, sum_readability, sum_maintainability
            nonlocal processed_count, failed_count

            async with semaphore:
                try:
                    rel_name = file_path.relative_to(extract_folder).as_posix()
                    code_text = file_path.read_text(encoding="utf-8", errors="replace")

                    # Run static analysis (CPU-bound, no DB needed)
                    report = analyze_code(code=code_text, filename=rel_name, language="python")

                    # Persist Review — serialised through db_lock to prevent
                    # concurrent SQLAlchemy session conflicts.
                    async with db_lock:
                        saved_review = await review_repository.create_review(
                            db=db,
                            user_id=user.id,
                            language="python",
                            filename=rel_name,
                            source_code=code_text,
                            summary=report.summary,
                            readability_score=report.scores.readability,
                            security_score=report.scores.security,
                            complexity_score=report.scores.complexity,
                            maintainability_score=report.scores.maintainability,
                            overall_score=report.scores.overall,
                            favorite=False,
                        )
                        reviewed_items.append(HistoryItem.model_validate(saved_review))
                        processed_count += 1

                    # Update running stats (pure Python, no I/O)
                    total_issues += len(report.issues)
                    critical_issues += sum(1 for iss in report.issues if iss.severity in {"CRITICAL", "HIGH"})
                    sum_overall += report.scores.overall or 0.0
                    sum_security += report.scores.security or 0.0
                    sum_complexity += report.scores.complexity or 0.0
                    sum_readability += report.scores.readability or 0.0
                    sum_maintainability += report.scores.maintainability or 0.0

                    # Update task progress periodically (DB locked)
                    if processed_count % 3 == 0 or processed_count == len(python_files):
                        async with db_lock:
                            await task_repository.update_progress(
                                db,
                                task,
                                processed_files=processed_count,
                                failed_files=failed_count,
                            )

                except Exception as exc:
                    failed_count += 1
                    logger.error("Error analyzing project file %s: %s", file_path.name, str(exc))


        # Execute concurrent tasks then commit all flushed progress in one shot
        analysis_tasks = [analyze_single_file(p) for p in python_files]
        await asyncio.gather(*analysis_tasks)
        await db.commit()

        n = max(processed_count, 1)
        avg_overall = round(sum_overall / n, 2)
        avg_security = round(sum_security / n, 2)
        avg_complexity = round(sum_complexity / n, 2)
        avg_readability = round(sum_readability / n, 2)
        avg_maintainability = round(sum_maintainability / n, 2)

        ast_metrics.average_complexity = avg_complexity
        ast_metrics.average_security_score = avg_security
        ast_metrics.average_readability = avg_readability
        ast_metrics.average_maintainability = avg_maintainability
        ast_metrics.critical_findings_count = critical_issues

        # Summary assessments
        sec_summary = (
            "Robust security posture with zero critical findings."
            if critical_issues == 0
            else f"Identified {critical_issues} high or critical priority vulnerability patterns requiring remediation."
        )
        comp_summary = (
            f"Average Maintainability Index of {avg_maintainability}/100 across {processed_count} files."
        )
        doc_summary = (
            f"Scanned {len(packages)} top-level packages. Average readability index: {avg_readability}/100."
        )

        response = BatchReviewResponse(
            task_id=task.id,
            status="COMPLETED",
            overall_project_score=avg_overall,
            total_files_analyzed=processed_count,
            total_issues=total_issues,
            critical_issues=critical_issues,
            security_summary=sec_summary,
            complexity_summary=comp_summary,
            documentation_summary=doc_summary,
            average_readability=avg_readability,
            average_maintainability=avg_maintainability,
            project_metrics=ast_metrics,
            directory_tree=tree,
            file_reviews=reviewed_items,
        )

        # 4. Generate and save project report
        report_id = await report_service.generate_and_save_report(response, project_name=project_name)
        response.report_id = report_id

        # 5. Mark task completed
        duration = time.perf_counter() - start_time
        await task_repository.mark_completed(
            db,
            task,
            output_path=f"app/uploads/reports/{report_id}",
            processing_time=duration,
        )

        # 6. Cleanup extracted directory
        cleanup_directory(extract_folder)

        try:
            from app.core.audit import log_audit_background
            from app.core.metrics import metrics_collector
            from app.services.webhook_service import webhook_service

            metrics_collector.record_batch_job(status="completed")
            asyncio.create_task(
                webhook_service.broadcast_event_background(
                    event_type="batch.completed",
                    payload_data={
                        "task_id": str(task.id),
                        "project_name": project_name,
                        "report_id": report_id,
                        "overall_score": avg_overall,
                        "total_files": len(reviewed_items),
                    },
                )
            )
            asyncio.create_task(
                log_audit_background(
                    action="batch.analysis_completed",
                    resource="batch",
                    user_id=user.id,
                    resource_id=str(task.id),
                    status="success",
                    metadata={"project_name": project_name, "score": avg_overall, "total_files": len(reviewed_items)},
                )
            )
        except Exception:
            pass

        logger.info(
            "Project batch analysis completed: task=%s project=%s score=%s duration=%ss",
            task.id,
            project_name,
            avg_overall,
            round(duration, 2),
        )

        return response

    async def run_project_analysis_background(
        self,
        user_id: uuid.UUID,
        zip_file_path: Path,
        project_name: str,
        task_id: uuid.UUID,
    ):
        """Asynchronous background worker function invoked by FastAPI BackgroundTasks."""
        async with AsyncSessionLocal() as db:
            from app.repositories.user_repository import user_repository

            user = await user_repository.get_by_id(db, user_id)
            task = await task_repository.get_by_id(db, task_id)
            if not user or not task:
                return

            try:
                await self.execute_project_pipeline(
                    db=db,
                    user=user,
                    zip_file_path=zip_file_path,
                    project_name=project_name,
                    task=task,
                )
            except Exception as exc:
                logger.error("Background project analysis task failed: %s", str(exc))
                await task_repository.mark_failed(db, task, str(exc))
            finally:
                # Cleanup temp zip
                if zip_file_path.exists():
                    try:
                        zip_file_path.unlink()
                    except Exception:
                        pass


batch_service = BatchService()
