"""
Chapter management: listing, reading, and saving chapters.
Uses the naming system for standardized file operations.
"""

import re
from pathlib import Path
from typing import Any

from backend.core.naming import (
    ChapterId,
    ChapterType,
    scan_chapters,
    scan_chapter_workspaces,
    scan_drafts,
)
from backend.core.project_manager import get_project_path
from backend.models.chapter import (
    ChapterContent,
    ChapterListItem,
    ChapterMetadata,
    ChapterWorkspaceFileContent,
    ChapterWorkspaceFileItem,
    ChapterWorkspaceFileKey,
    ChapterWorkspaceListItem,
)
from backend.utils.frontmatter import build_frontmatter
from backend.utils.logging_config import logger

_WORKSPACE_FILE_LABELS: dict[ChapterWorkspaceFileKey, str] = {
    "outline": "章纲",
    "concept": "构思",
    "draft": "草稿",
}

_WORKSPACE_FILENAMES: dict[ChapterWorkspaceFileKey, str] = {
    "outline": "outline.md",
    "concept": "concept.md",
    "draft": "draft.md",
}


def _chapters_root(slug: str) -> Path:
    return get_project_path(slug) / "chapters"


def _drafts_root(slug: str) -> Path:
    return get_project_path(slug) / "drafts"


def _count_words(text: str) -> int:
    """Count words in text. For CJK text, count characters; for Latin, count spaces."""
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))
    latin_text = re.sub(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", " ", text)
    latin_words = len(latin_text.split())
    return cjk_chars + latin_words


def _workspace_file_path(drafts_root: Path, chapter_id: ChapterId, file_key: ChapterWorkspaceFileKey) -> Path:
    filename = _WORKSPACE_FILENAMES[file_key]
    return chapter_id.to_draft_dir(drafts_root) / filename


def _build_workspace_file_item(draft_dir: Path, file_key: ChapterWorkspaceFileKey) -> ChapterWorkspaceFileItem:
    filename = _WORKSPACE_FILENAMES[file_key]
    filepath = draft_dir / filename
    word_count = 0
    if filepath.exists():
        word_count = _count_words(filepath.read_text(encoding="utf-8"))

    return ChapterWorkspaceFileItem(
        key=file_key,
        filename=filename,
        label=_WORKSPACE_FILE_LABELS[file_key],
        exists=filepath.exists(),
        word_count=word_count,
    )


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
            if c.volume == volume
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


def list_drafts(slug: str, volume: int | None = None) -> list[ChapterListItem]:
    """
    List all chapter drafts for a project.
    Drafts are stored in nested directories: drafts/vol{V}/{Type}_vol{V}_ch{N}/draft.md
    """
    root = _drafts_root(slug)
    all_drafts = scan_drafts(root)

    if volume is not None:
        all_drafts = [
            c for c in all_drafts
            if c.volume == volume
        ]

    items = []
    for chapter_id in all_drafts:
        draft_dir = chapter_id.to_draft_dir(root)
        filepath = draft_dir / "draft.md"
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


def list_chapter_workspaces(slug: str, volume: int | None = None) -> list[ChapterWorkspaceListItem]:
    """List chapter workspaces that contain outline/concept/draft files."""
    root = _drafts_root(slug)
    workspaces = scan_chapter_workspaces(root)

    if volume is not None:
        workspaces = [
            c for c in workspaces
            if c.volume == volume
        ]

    items: list[ChapterWorkspaceListItem] = []
    for chapter_id in workspaces:
        draft_dir = chapter_id.to_draft_dir(root)
        items.append(
            ChapterWorkspaceListItem(
                type=chapter_id.type,
                volume=chapter_id.volume,
                number=chapter_id.number,
                display_name=chapter_id.display_name(),
                draft_dir=str(draft_dir),
                files=[
                    _build_workspace_file_item(draft_dir, "outline"),
                    _build_workspace_file_item(draft_dir, "concept"),
                    _build_workspace_file_item(draft_dir, "draft"),
                ],
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


def read_draft_content(slug: str, chapter_id: ChapterId) -> ChapterContent:
    """
    Read the full content of a chapter draft.
    Drafts are stored in nested directories: drafts/vol{V}/{Type}_vol{V}_ch{N}/draft.md
    """
    root = _drafts_root(slug)
    filepath = _workspace_file_path(root, chapter_id, "draft")

    if not filepath.exists():
        raise FileNotFoundError(f"Chapter draft not found: {filepath}")

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


def read_chapter_workspace_file(
    slug: str,
    chapter_id: ChapterId,
    file_key: ChapterWorkspaceFileKey,
) -> ChapterWorkspaceFileContent:
    """Read a specific file from a chapter workspace."""
    root = _drafts_root(slug)
    draft_dir = chapter_id.to_draft_dir(root)
    filepath = _workspace_file_path(root, chapter_id, file_key)

    if not draft_dir.exists():
        raise FileNotFoundError(f"Chapter workspace not found: {draft_dir}")

    if not filepath.exists():
        return ChapterWorkspaceFileContent(
            type=chapter_id.type,
            volume=chapter_id.volume,
            number=chapter_id.number,
            display_name=chapter_id.display_name(),
            file_key=file_key,
            filename=_WORKSPACE_FILENAMES[file_key],
            content="",
            exists=False,
            word_count=0,
        )

    content = filepath.read_text(encoding="utf-8")
    return ChapterWorkspaceFileContent(
        type=chapter_id.type,
        volume=chapter_id.volume,
        number=chapter_id.number,
        display_name=chapter_id.display_name(),
        file_key=file_key,
        filename=_WORKSPACE_FILENAMES[file_key],
        content=content,
        exists=True,
        word_count=_count_words(content),
    )


def save_chapter_workspace_file(
    slug: str,
    chapter_id: ChapterId,
    file_key: ChapterWorkspaceFileKey,
    content: str,
) -> str:
    """Save a file into a chapter workspace, creating directories as needed."""
    root = _drafts_root(slug)
    draft_dir = chapter_id.to_draft_dir(root)
    draft_dir.mkdir(parents=True, exist_ok=True)

    filepath = _workspace_file_path(root, chapter_id, file_key)
    filepath.write_text(content, encoding="utf-8")
    logger.info(f"Saved chapter workspace file: {filepath}")
    return str(filepath)


def save_chapter_draft(
    slug: str,
    chapter_id: ChapterId,
    content: str,
) -> str:
    """
    Save a chapter draft, backing up any existing file.
    Drafts are stored in nested directories: drafts/vol{V}/{Type}_vol{V}_ch{N}/draft.md

    Returns the path of the saved file.
    """
    root = _drafts_root(slug)
    draft_dir = chapter_id.to_draft_dir(root)
    draft_dir.mkdir(parents=True, exist_ok=True)

    filepath = _workspace_file_path(root, chapter_id, "draft")

    if filepath.exists():
        backup_path = draft_dir / "draft_bak.md"
        filepath.replace(backup_path)
        logger.info(f"Backed up existing draft to {backup_path}")

    filepath.write_text(content, encoding="utf-8")
    logger.info(f"Saved draft: {filepath}")
    return str(filepath)


def submit_draft_to_chapter(
    slug: str,
    chapter_id: ChapterId,
) -> dict[str, Any]:
    """
    Submit a draft to become a formal chapter and convert to DOCX.

    Steps:
    1. Read draft content from drafts/vol{V}/{Type}_vol{V}_ch{N}/draft.md
    2. Save as formal chapter in chapters/vol{V}/{Type}.{NNN}.md with frontmatter
    3. Convert MD to DOCX and save in source/vol{V}/{Type}.{NNN}.docx
    4. Keep draft as backup (do not delete)

    Returns dict with chapter_path and docx_path.

    Raises:
        FileNotFoundError: If draft does not exist.
    """
    project_path = get_project_path(slug)

    # 1. Read draft content
    draft_filepath = _workspace_file_path(_drafts_root(slug), chapter_id, "draft")
    if not draft_filepath.exists():
        raise FileNotFoundError(f"Draft not found: {draft_filepath}")

    draft_content = draft_filepath.read_text(encoding="utf-8")

    # 2. Save as formal chapter with frontmatter
    chapters_root = _chapters_root(slug)
    chapter_filepath = chapter_id.to_path(chapters_root)
    chapter_filepath.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "title": chapter_id.display_name(),
        "type": chapter_id.type.value,
        "volume": chapter_id.volume,
        "number": chapter_id.number,
        "source": "draft_submission",
    }
    full_content = build_frontmatter(metadata, draft_content)
    chapter_filepath.write_text(full_content, encoding="utf-8")
    logger.info(f"Submitted draft to chapter: {chapter_filepath}")

    # 3. Convert MD to DOCX and save in source/
    source_dir = project_path / "source"
    if chapter_id.type == ChapterType.EXTRA:
        vol_source_dir = source_dir / "extras"
    else:
        vol_source_dir = source_dir / f"vol{chapter_id.volume}"
    vol_source_dir.mkdir(parents=True, exist_ok=True)

    docx_filename = chapter_id.to_filename().replace(".md", ".docx")
    docx_filepath = vol_source_dir / docx_filename

    from backend.utils.md_to_docx import convert_md_to_docx
    convert_md_to_docx(
        md_path=str(draft_filepath),
        docx_path=str(docx_filepath),
        title=chapter_id.display_name(),
    )
    logger.info(f"Converted chapter to DOCX: {docx_filepath}")

    return {
        "chapter_path": str(chapter_filepath),
        "docx_path": str(docx_filepath),
        "word_count": _count_words(draft_content),
    }
