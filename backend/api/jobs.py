"""
Batch job REST API endpoints.
"""

from fastapi import APIRouter, HTTPException

from backend.core import job_manager
from backend.models.job import CalculateBatchesRequest, CalculateBatchesResponse, ClaimBatchResponse, JobInfo

router = APIRouter(prefix="/projects/{slug}/jobs", tags=["jobs"])


@router.post("/calculate", response_model=CalculateBatchesResponse)
async def calculate_batches(slug: str, request: CalculateBatchesRequest):
    """Calculate chapter batches for a volume."""
    try:
        return job_manager.calculate_batches(
            slug, request.volume, request.max_chars,
            request.start_chapter, request.end_chapter,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/claim", response_model=ClaimBatchResponse)
async def claim_next_batch(slug: str, job_id: str):
    """Claim the next batch in a job."""
    try:
        return job_manager.claim_next_batch(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[JobInfo])
async def list_jobs(slug: str):
    """List active jobs for this project."""
    return job_manager.list_jobs(slug)


@router.delete("/{job_id}", status_code=204)
async def cancel_job(slug: str, job_id: str):
    """Cancel a running job."""
    job_manager.cancel_job(job_id)
