"""
Pydantic models for lore management.
"""

from typing import Any

from pydantic import BaseModel, Field


class LoreEntry(BaseModel):
    """A single lore database entry."""

    id: str  # Relative path: "characters/束.md"
    name: str
    category: str
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class LoreEntryDetail(BaseModel):
    """Full lore entry with content."""

    id: str
    name: str
    category: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    content: str  # Full body content


class LoreSnapshot(BaseModel):
    """Overview of all lore entries."""

    entries: list[LoreEntry]
    total: int


class LoreSearchResult(BaseModel):
    """Search result from lore database."""

    id: str
    name: str
    category: str
    excerpt: str  # Matching context
    score: float = 0.0


class LorePatchUpdate(BaseModel):
    """A single update within a patch."""

    type: str = "update"  # "new" or "update"
    category: str
    name: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = ""  # e.g., "vol1/ch005"


class LorePatchRequest(BaseModel):
    """Request to propose a lore patch."""

    lore_updates: list[LorePatchUpdate]


class PatchReview(BaseModel):
    """Review data for a proposed patch."""

    patch_id: str
    diff_text: str
    update_count: int


class CommitResult(BaseModel):
    """Result of committing a patch."""

    updated_files: list[str]
    git_sha: str | None = None


class LoreUpdateRequest(BaseModel):
    """Request body for direct lore entry update."""

    content: str
    metadata: dict[str, Any] | None = None
