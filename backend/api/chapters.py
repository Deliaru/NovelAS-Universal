"""
Chapter management REST API endpoints.
"""

from typing import cast

from fastapi import APIRouter, HTTPException, Query

from backend.core import chapter_manager
from backend.core.naming import ChapterId, ChapterType
from backend.models.chapter import (
    ChapterContent,
    ChapterListItem,
    ChapterMetadata,
    ChapterWorkspaceFileContent,
    ChapterWorkspaceFileKey,
    ChapterWorkspaceListItem,
    SaveDraftRequest,
)

router = APIRouter(prefix="/projects/{slug}/chapters", tags=["chapters"])


def _parse_workspace_file_key(file_key: str) -> ChapterWorkspaceFileKey:
    if file_key not in {"outline", "concept", "draft"}:
        raise HTTPException(status_code=400, detail=f"Unsupported workspace file: {file_key}")
    return cast(ChapterWorkspaceFileKey, file_key)


@router.get("", response_model=list[ChapterListItem])
async def list_chapters(slug: str, volume: int | None = None):
    """List all chapters, optionally filtered by volume."""
    try:
        return chapter_manager.list_chapters(slug, volume=volume)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/outlines", response_model=list[ChapterWorkspaceListItem])
async def list_chapter_outlines(slug: str, volume: int | None = None):
    """List chapter workspaces that contain outline/concept/draft files."""
    try:
        return chapter_manager.list_chapter_workspaces(slug, volume=volume)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/outlines/{chapter_type}/{number}/{file_key}", response_model=ChapterWorkspaceFileContent)
async def read_chapter_outline_file(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    file_key: str,
    volume: int = Query(default=1, description="Volume number (ignored for Extra)"),
):
    """Read outline or concept content from a chapter workspace."""
    parsed_file_key = _parse_workspace_file_key(file_key)

    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        return chapter_manager.read_chapter_workspace_file(slug, chapter_id, parsed_file_key)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/outlines/{chapter_type}/{number}/{file_key}")
async def save_chapter_outline_file(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    file_key: str,
    request: SaveDraftRequest,
    volume: int = Query(default=1),
):
    """Save outline or concept content into a chapter workspace."""
    parsed_file_key = _parse_workspace_file_key(file_key)

    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        path = chapter_manager.save_chapter_workspace_file(slug, chapter_id, parsed_file_key, request.content)
        return {"status": "ok", "path": path}
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


@router.get("/drafts", response_model=list[ChapterListItem])
async def list_drafts(slug: str, volume: int | None = None):
    """List all chapter drafts, optionally filtered by volume."""
    try:
        return chapter_manager.list_drafts(slug, volume=volume)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/drafts/{chapter_type}/{number}", response_model=ChapterContent)
async def read_draft_content(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    volume: int = Query(default=1, description="Volume number (ignored for Extra)"),
):
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


@router.post("/drafts/{chapter_type}/{number}/submit")
async def submit_draft(
    slug: str,
    chapter_type: ChapterType,
    number: int,
    volume: int = Query(default=1, description="Volume number (ignored for Extra)"),
):
    """Submit a draft to become a formal chapter and convert to DOCX."""
    try:
        chapter_id = ChapterId(
            type=chapter_type,
            volume=0 if chapter_type == ChapterType.EXTRA else volume,
            number=number,
        )
        result = chapter_manager.submit_draft_to_chapter(slug, chapter_id)
        return {
            "status": "ok",
            "chapter_path": result["chapter_path"],
            "docx_path": result["docx_path"],
            "word_count": result["word_count"],
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
