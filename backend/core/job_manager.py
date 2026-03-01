"""
Batch processing job manager with breakpoint resume support.
Ported from NovelAS novel_mcp_server.py calculate_chapter_batches / claim_next_batch.
"""

import json
import uuid
from pathlib import Path

from backend.config import settings
from backend.core.naming import ChapterId, ChapterType, scan_chapters
from backend.core.project_manager import get_project_path
from backend.models.job import (
    BatchInfo,
    CalculateBatchesResponse,
    ClaimBatchResponse,
    JobInfo,
)
from backend.utils.logging_config import logger

# Jobs cache file at application level
JOBS_CACHE_FILE = settings.app_root / "data" / "jobs_cache.json"


def _load_jobs_cache() -> dict:
    """Load the jobs cache file."""
    if not JOBS_CACHE_FILE.exists():
        return {}
    try:
        return json.loads(JOBS_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_jobs_cache(cache: dict) -> None:
    """Save the jobs cache file."""
    JOBS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    JOBS_CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def calculate_batches(
    slug: str,
    volume: int,
    max_chars: int = 50000,
    start_chapter: int | None = None,
    end_chapter: int | None = None,
) -> CalculateBatchesResponse:
    """
    Calculate chapter batches for a volume based on character limits.

    Returns batch info. If multiple batches are needed, creates a job with
    a persistent job_id for resume support.
    """
    chapters_root = get_project_path(slug) / "chapters"
    all_chapters = scan_chapters(chapters_root)

    # Filter to requested volume and chapter range
    filtered = []
    for c in all_chapters:
        if c.type == ChapterType.EXTRA:
            continue  # Extras are global, not per-volume
        if c.volume != volume:
            continue
        if c.type == ChapterType.CHAPTER:
            if start_chapter is not None and c.number < start_chapter:
                continue
            if end_chapter is not None and c.number > end_chapter:
                continue
        filtered.append(c)

    # Read file sizes and bin into batches
    batches: list[BatchInfo] = []
    current_batch_chapters: list[str] = []
    current_batch_chars = 0

    for chapter_id in filtered:
        filepath = chapter_id.to_path(chapters_root)
        if not filepath.exists():
            continue
        file_chars = len(filepath.read_text(encoding="utf-8"))

        if current_batch_chars + file_chars > max_chars and current_batch_chapters:
            batches.append(BatchInfo(
                chapters=current_batch_chapters,
                total_chars=current_batch_chars,
            ))
            current_batch_chapters = []
            current_batch_chars = 0

        current_batch_chapters.append(chapter_id.to_filename())
        current_batch_chars += file_chars

    if current_batch_chapters:
        batches.append(BatchInfo(
            chapters=current_batch_chapters,
            total_chars=current_batch_chars,
        ))

    # Create job if multiple batches
    job_id = None
    message = f"Volume {volume}: {len(batches)} batch(es)"

    if len(batches) > 1:
        job_id = uuid.uuid4().hex[:8]
        cache = _load_jobs_cache()
        cache[job_id] = JobInfo(
            job_id=job_id,
            project_slug=slug,
            volume=volume,
            batches=batches,
            current_index=0,
            status="active",
        ).model_dump()
        _save_jobs_cache(cache)
        message = f"Created job {job_id} with {len(batches)} batches"

    logger.info(message)
    return CalculateBatchesResponse(
        volume=volume,
        total_batches=len(batches),
        batches=batches,
        job_id=job_id,
        message=message,
    )


def claim_next_batch(job_id: str) -> ClaimBatchResponse:
    """
    Claim the next unprocessed batch in a job.

    Raises:
        KeyError: If job_id not found.
    """
    cache = _load_jobs_cache()
    if job_id not in cache:
        raise KeyError(f"Job {job_id} not found")

    job = JobInfo(**cache[job_id])
    idx = job.current_index

    if idx >= len(job.batches):
        # All batches processed
        del cache[job_id]
        _save_jobs_cache(cache)
        return ClaimBatchResponse(
            status="completed",
            job_id=job_id,
            batch_index=idx,
            chapters=[],
            is_last_batch=True,
            total_batches=len(job.batches),
        )

    batch = job.batches[idx]
    is_last = idx + 1 >= len(job.batches)

    # Increment counter
    job.current_index = idx + 1
    if is_last:
        job.status = "completed"
        del cache[job_id]
    else:
        cache[job_id] = job.model_dump()
    _save_jobs_cache(cache)

    return ClaimBatchResponse(
        status="ok",
        job_id=job_id,
        batch_index=idx,
        chapters=batch.chapters,
        is_last_batch=is_last,
        total_batches=len(job.batches),
    )


def list_jobs(slug: str | None = None) -> list[JobInfo]:
    """List all active jobs, optionally filtered by project."""
    cache = _load_jobs_cache()
    jobs = [JobInfo(**v) for v in cache.values()]
    if slug:
        jobs = [j for j in jobs if j.project_slug == slug]
    return jobs


def cancel_job(job_id: str) -> None:
    """Cancel and remove a job."""
    cache = _load_jobs_cache()
    if job_id in cache:
        del cache[job_id]
        _save_jobs_cache(cache)
        logger.info(f"Cancelled job {job_id}")
