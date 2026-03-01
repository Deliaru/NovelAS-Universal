"""
Lore management REST API endpoints.
"""

from fastapi import APIRouter, HTTPException

from backend.core import lore_manager
from backend.models.lore import (
    CommitResult,
    LoreEntryDetail,
    LorePatchRequest,
    LoreSearchResult,
    LoreSnapshot,
    PatchReview,
)

router = APIRouter(prefix="/projects/{slug}/lore", tags=["lore"])


@router.get("/snapshot", response_model=LoreSnapshot)
async def get_snapshot(slug: str):
    """Get overview of all lore entries."""
    try:
        return lore_manager.get_snapshot(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/details", response_model=list[LoreEntryDetail])
async def get_entry_details(slug: str, entry_ids: list[str]):
    """Get full details for specific lore entries."""
    try:
        return lore_manager.get_entry_details(slug, entry_ids)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/search", response_model=list[LoreSearchResult])
async def search_lore(slug: str, keyword: str, category: str | None = None):
    """Search lore database by keyword."""
    try:
        return lore_manager.search_lore(slug, keyword, category)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/patch/propose", response_model=PatchReview)
async def propose_patch(slug: str, request: LorePatchRequest):
    """Propose a lore patch (stage for review)."""
    try:
        return lore_manager.propose_patch(slug, request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/patch/{patch_id}/commit", response_model=CommitResult)
async def commit_patch(slug: str, patch_id: str):
    """Commit a pending lore patch."""
    try:
        return lore_manager.commit_patch(slug, patch_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/patch/{patch_id}", status_code=204)
async def reject_patch(slug: str, patch_id: str):
    """Reject and discard a pending patch."""
    lore_manager.reject_patch(slug, patch_id)


@router.put("/{category}/{name}")
async def update_entry(
    slug: str,
    category: str,
    name: str,
    content: str,
    metadata: dict | None = None,
):
    """Direct update of a lore entry (for GUI editing)."""
    try:
        path = lore_manager.update_lore_entry(slug, category, name, content, metadata)
        return {"status": "ok", "path": path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history/{category}/{name}")
async def get_entry_history(slug: str, category: str, name: str):
    """Get Git commit history for a lore entry."""
    from backend.core.project_manager import get_project_path
    from backend.utils.git_ops import get_file_history

    try:
        project_path = get_project_path(slug)
        rel_path = f"lore_database/{category}/{name}.md"
        return get_file_history(project_path, rel_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
