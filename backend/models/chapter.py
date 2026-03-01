"""
Pydantic models for chapter management.
"""

from pydantic import BaseModel

from backend.core.naming import ChapterType


class ChapterListItem(BaseModel):
    """Lightweight chapter info for listing."""

    type: ChapterType
    volume: int
    number: int
    filename: str
    display_name: str
    word_count: int = 0


class ChapterMetadata(BaseModel):
    """Chapter metadata including file stats."""

    type: ChapterType
    volume: int
    number: int
    filename: str
    display_name: str
    path: str
    word_count: int = 0
    char_count: int = 0


class ChapterContent(BaseModel):
    """Full chapter content with metadata."""

    type: ChapterType
    volume: int
    number: int
    filename: str
    display_name: str
    content: str
    word_count: int = 0


class SaveDraftRequest(BaseModel):
    """Request body for saving a chapter draft."""

    content: str
