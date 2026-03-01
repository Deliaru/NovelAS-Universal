"""
Knowledge file management.
Distinguishes between:
- Shared knowledge (knowledge/): writing theory, universal guides
- Project knowledge (projects/{slug}/knowledge/): project-specific guides, recaps
"""

from pathlib import Path

from backend.config import settings
from backend.core.project_manager import get_project_path
from backend.utils.logging_config import logger


def _shared_knowledge_dir() -> Path:
    return settings.get_knowledge_dir()


def _project_knowledge_dir(slug: str) -> Path:
    return get_project_path(slug) / "knowledge"


def list_shared_knowledge() -> list[dict]:
    """List all shared knowledge files."""
    root = _shared_knowledge_dir()
    if not root.exists():
        return []

    return [
        {
            "path": str(f.relative_to(root)),
            "name": f.stem,
            "size": f.stat().st_size,
        }
        for f in sorted(root.rglob("*.md"))
        if f.is_file()
    ]


def list_project_knowledge(slug: str) -> list[dict]:
    """List all project-specific knowledge files."""
    root = _project_knowledge_dir(slug)
    if not root.exists():
        return []

    return [
        {
            "path": str(f.relative_to(root)),
            "name": f.stem,
            "size": f.stat().st_size,
        }
        for f in sorted(root.rglob("*.md"))
        if f.is_file()
    ]


def read_knowledge_file(
    path: str,
    slug: str | None = None,
) -> str:
    """
    Read a knowledge file.

    If slug is provided, looks in project knowledge first, then shared.
    If slug is None, only looks in shared knowledge.
    """
    if slug:
        project_file = _project_knowledge_dir(slug) / path
        if project_file.exists():
            return project_file.read_text(encoding="utf-8")

    shared_file = _shared_knowledge_dir() / path
    if shared_file.exists():
        return shared_file.read_text(encoding="utf-8")

    raise FileNotFoundError(f"Knowledge file not found: {path}")


def update_knowledge_file(
    path: str,
    content: str,
    slug: str | None = None,
) -> str:
    """
    Create or update a knowledge file.

    If slug is provided, writes to project knowledge.
    Otherwise writes to shared knowledge.
    """
    if slug:
        root = _project_knowledge_dir(slug)
    else:
        root = _shared_knowledge_dir()

    filepath = root / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

    logger.info(f"Updated knowledge file: {filepath}")
    return str(filepath)
