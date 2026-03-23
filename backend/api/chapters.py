"""
Chapter management REST API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.core import chapter_manager
from backend.core.naming import ChapterId, ChapterType
from backend.models.chapter import (
    ChapterContent,
    ChapterListItem,
    ChapterMetadata,
    SaveDraftRequest,
)

router = APIRouter(prefix="/projects/{slug}/chapters", tags=["chapters"])


@router.get("", response_model=list[ChapterListItem])
async def list_chapters(slug: str, volume: int | None = None):
    """List all chapters, optionally filtered by volume."""
    try:
        return chapter_manager.list_chapters(slug, volume=volume)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{chapter_type}/{number}", response_model=ChapterContent)
async def read_chapter(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    volume: int = Query(default=1, description="Volume number (ignored for Extra)"),
):
    """Read the full content of a chapter."""
    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        return chapter_manager.read_chapter_content(slug, chapter_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{chapter_type}/{number}/metadata", response_model=ChapterMetadata)
async def read_chapter_metadata(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    volume: int = Query(default=1),
):
    """Read chapter metadata (word count, path, etc.)."""
    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        return chapter_manager.read_chapter_metadata(slug, chapter_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{chapter_type}/{number}/draft")
async def save_draft(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    request: SaveDraftRequest,
    volume: int = Query(default=1),
):
    """Save a chapter draft."""
    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        path = chapter_manager.save_chapter_draft(slug, chapter_id, request.content)
        return {"status": "ok", "path": path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/drafts")
async def list_drafts(slug: str, volume: int | None = None) -> list[ChapterListItem]:
    """List all chapter drafts, optionally filtered by volume."""
    try:
        return chapter_manager.list_drafts(slug, volume=volume)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/drafts/{chapter_type}/{number}")
async def read_draft_content(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    volume: int = Query(default=1, description="Volume number (ignored for Extra)"),
) -> ChapterContent:
    """Read the full content of a chapter draft."""
    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        return chapter_manager.read_draft_content(slug, chapter_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
