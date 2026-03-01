"""
Chapter management: listing, reading, and saving chapters.
Uses the naming system for standardized file operations.
"""

import re
from pathlib import Path

from backend.core.naming import ChapterId, ChapterType, parse_filename, scan_chapters
from backend.core.project_manager import get_project_path
from backend.models.chapter import ChapterContent, ChapterListItem, ChapterMetadata
from backend.utils.logging_config import logger


def _chapters_root(slug: str) -> Path:
    return get_project_path(slug) / "chapters"


def _drafts_root(slug: str) -> Path:
    return get_project_path(slug) / "drafts"


def _count_words(text: str) -> int:
    """Count words in text. For CJK text, count characters; for Latin, count spaces."""
    # Count CJK characters
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))
    # Count Latin words
    latin_text = re.sub(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", " ", text)
    latin_words = len(latin_text.split())
    return cjk_chars + latin_words


def list_chapters(slug: str, volume: int | None = None) -> list[ChapterListItem]:
    """
    List all chapters for a project, optionally filtered by volume.

    Returns sorted list of chapter summaries.
    """
    root = _chapters_root(slug)
    all_chapters = scan_chapters(root)

    if volume is not None:
        all_chapters = [
            c for c in all_chapters
            if c.volume == volume or c.type == ChapterType.EXTRA
        ]

    items = []
    for chapter_id in all_chapters:
        filepath = chapter_id.to_path(root)
        word_count = 0
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            word_count = _count_words(content)

        items.append(
            ChapterListItem(
                type=chapter_id.type,
                volume=chapter_id.volume,
                number=chapter_id.number,
                filename=chapter_id.to_filename(),
                display_name=chapter_id.display_name(),
                word_count=word_count,
            )
        )

    return items


def read_chapter_metadata(slug: str, chapter_id: ChapterId) -> ChapterMetadata:
    """
    Read chapter file metadata (size, word count, path).

    Raises:
        FileNotFoundError: If chapter file doesn't exist.
    """
    root = _chapters_root(slug)
    filepath = chapter_id.to_path(root)

    if not filepath.exists():
        raise FileNotFoundError(f"Chapter not found: {chapter_id.to_filename()}")

    content = filepath.read_text(encoding="utf-8")
    return ChapterMetadata(
        type=chapter_id.type,
        volume=chapter_id.volume,
        number=chapter_id.number,
        filename=chapter_id.to_filename(),
        display_name=chapter_id.display_name(),
        path=str(filepath),
        word_count=_count_words(content),
        char_count=len(content),
    )


def read_chapter_content(slug: str, chapter_id: ChapterId) -> ChapterContent:
    """
    Read the full content of a chapter.

    Raises:
        FileNotFoundError: If chapter file doesn't exist.
    """
    root = _chapters_root(slug)
    filepath = chapter_id.to_path(root)

    if not filepath.exists():
        raise FileNotFoundError(f"Chapter not found: {chapter_id.to_filename()}")

    content = filepath.read_text(encoding="utf-8")
    return ChapterContent(
        type=chapter_id.type,
        volume=chapter_id.volume,
        number=chapter_id.number,
        filename=chapter_id.to_filename(),
        display_name=chapter_id.display_name(),
        content=content,
        word_count=_count_words(content),
    )


def save_chapter_draft(
    slug: str,
    chapter_id: ChapterId,
    content: str,
) -> str:
    """
    Save a chapter draft, backing up any existing file.

    Returns the path of the saved file.
    """
    drafts = _drafts_root(slug)
    if chapter_id.type == ChapterType.EXTRA:
        draft_dir = drafts / "extras"
    else:
        draft_dir = drafts / f"vol{chapter_id.volume}"
    draft_dir.mkdir(parents=True, exist_ok=True)

    filepath = draft_dir / chapter_id.to_filename()

    # Backup existing file
    if filepath.exists():
        backup_name = filepath.stem + "_bak" + filepath.suffix
        backup_path = draft_dir / backup_name
        filepath.rename(backup_path)
        logger.info(f"Backed up existing draft to {backup_path}")

    filepath.write_text(content, encoding="utf-8")
    logger.info(f"Saved draft: {filepath}")
    return str(filepath)
