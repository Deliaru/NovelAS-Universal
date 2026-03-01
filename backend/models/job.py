"""
Pydantic models for batch processing jobs.
"""

from pydantic import BaseModel, Field


class BatchInfo(BaseModel):
    """Information about a single batch within a job."""

    chapters: list[str]  # Chapter filenames in this batch
    total_chars: int = 0


class JobInfo(BaseModel):
    """Information about a batch processing job."""

    job_id: str
    project_slug: str
    volume: int
    batches: list[BatchInfo]
    current_index: int = 0
    status: str = "active"  # active, completed, cancelled


class CalculateBatchesRequest(BaseModel):
    """Request to calculate chapter batches."""

    volume: int
    max_chars: int = 50000
    start_chapter: int | None = None
    end_chapter: int | None = None


class CalculateBatchesResponse(BaseModel):
    """Response from batch calculation."""

    volume: int
    total_batches: int
    batches: list[BatchInfo]
    job_id: str | None = None
    message: str = ""


class ClaimBatchResponse(BaseModel):
    """Response when claiming the next batch."""

    status: str  # "ok", "completed"
    job_id: str
    batch_index: int
    chapters: list[str]
    is_last_batch: bool
    total_batches: int
