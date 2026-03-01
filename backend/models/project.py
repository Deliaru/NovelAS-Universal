"""
Pydantic models for project management.
"""

from pydantic import BaseModel, Field


class VolumeConfig(BaseModel):
    """Configuration for a single volume."""

    number: int
    title: str = ""
    source_dir: str = ""  # Relative to project root, e.g. "source/vol1"


class ProjectSettings(BaseModel):
    """Per-project settings."""

    language: str = "zh-CN"
    embedding_model: str = "all-MiniLM-L6-v2"
    ai_provider: str | None = None
    prohibited_words: list[str] = Field(default_factory=list)
    style_reference: str | None = None  # Path to style reference chapter


class ProjectConfig(BaseModel):
    """Full project configuration, stored as project.yaml."""

    name: str
    slug: str
    description: str = ""
    volumes: list[VolumeConfig] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectSummary(BaseModel):
    """Lightweight project info for listing."""

    slug: str
    name: str
    description: str = ""
    volume_count: int = 0
    chapter_count: int = 0
    lore_count: int = 0


class VolumeStats(BaseModel):
    """Statistics for a single volume."""

    number: int
    title: str = ""
    chapter_count: int = 0
    interlude_count: int = 0
    has_prologue: bool = False
    has_finale: bool = False
    word_count: int = 0


class ProjectStats(BaseModel):
    """Detailed project statistics."""

    slug: str
    name: str
    volumes: list[VolumeStats] = Field(default_factory=list)
    total_chapters: int = 0
    total_words: int = 0
    lore_entries: dict[str, int] = Field(default_factory=dict)  # category -> count
    vector_memory_count: int = 0


class CreateProjectRequest(BaseModel):
    """Request body for creating a new project."""

    name: str
    slug: str
    description: str = ""
    volumes: list[VolumeConfig] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
