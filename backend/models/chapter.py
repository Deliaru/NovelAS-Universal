"""
Pydantic models for chapter management.
"""

from typing import Literal

from pydantic import BaseModel

from backend.core.naming import ChapterType

ChapterWorkspaceFileKey = Literal["outline", "concept", "draft"]


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


class ChapterWorkspaceFileItem(BaseModel):
    """Single file status inside a chapter workspace."""

    key: ChapterWorkspaceFileKey
    filename: str
    label: str
    exists: bool
    word_count: int = 0


class ChapterWorkspaceListItem(BaseModel):
    """Chapter workspace summary for outline listing."""

    type: ChapterType
    volume: int
    number: int
    display_name: str
    draft_dir: str
    files: list[ChapterWorkspaceFileItem]


class ChapterWorkspaceFileContent(BaseModel):
    """Workspace file content for outline/concept editing."""

    type: ChapterType
    volume: int
    number: int
    display_name: str
    file_key: ChapterWorkspaceFileKey
    filename: str
    content: str
    exists: bool = True
    word_count: int = 0


class SaveDraftRequest(BaseModel):
    """Request body for saving chapter-related text content."""

    content: str
