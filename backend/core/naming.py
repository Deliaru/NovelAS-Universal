"""
Chapter naming convention system.

Replaces the old numeric encoding scheme (negative numbers for interludes,
< -100 for extras) with explicit type discrimination.

Naming rules:
  - Prologue.md           : One per volume, no number
  - Chapter.{NNN}.md      : Per-volume numbering, 0-padded, starts at 000
  - Interlude.{NNN}.md    : Per-volume numbering, 0-padded, starts at 000
  - Finale.md             : One per volume, no number
  - Extra.{NNN}.md        : GLOBAL numbering across all volumes, 0-padded

Storage:
  - Prologue, Chapter, Interlude, Finale → chapters/vol{N}/
  - Extra → chapters/extras/
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class ChapterType(str, Enum):
    """Types of chapters in the novel."""

    PROLOGUE = "Prologue"
    CHAPTER = "Chapter"
    INTERLUDE = "Interlude"
    EXTRA = "Extra"
    FINALE = "Finale"


# Sorting weight for chapter types within a volume
_TYPE_SORT_ORDER = {
    ChapterType.PROLOGUE: 0,
    ChapterType.CHAPTER: 1,
    ChapterType.INTERLUDE: 2,
    ChapterType.FINALE: 3,
    ChapterType.EXTRA: 4,
}

DRAFT_WORKSPACE_FILENAMES = ("outline.md", "concept.md", "draft.md")


@dataclass(frozen=True)
class ChapterId:
    """
    Unique identifier for a chapter.

    Attributes:
        type: The chapter type (Prologue, Chapter, etc.)
        volume: Volume number (0 for extras, 1+ for volumes)
        number: Chapter number within its type/volume scope.
                For Prologue/Finale this is always 0.
                For Extra, this is the global sequential number.
    """

    type: ChapterType
    volume: int
    number: int = 0

    def to_filename(self) -> str:
        """Convert to the standardized filename."""
        if self.type == ChapterType.PROLOGUE:
            return "Prologue.md"
        elif self.type == ChapterType.FINALE:
            return "Finale.md"
        elif self.type == ChapterType.CHAPTER:
            return f"Chapter.{self.number:03d}.md"
        elif self.type == ChapterType.INTERLUDE:
            return f"Interlude.{self.number:03d}.md"
        elif self.type == ChapterType.EXTRA:
            return f"Extra.{self.number:03d}.md"
        raise ValueError(f"Unknown chapter type: {self.type}")

    def to_path(self, chapters_root: Path) -> Path:
        """
        Convert to the full file path.

        Args:
            chapters_root: The project's chapters/ directory.
        """
        if self.type == ChapterType.EXTRA:
            return chapters_root / "extras" / self.to_filename()
        return chapters_root / f"vol{self.volume}" / self.to_filename()

    def to_draft_dir(self, drafts_root: Path) -> Path:
        """
        Path to the draft subdirectory.

        Draft structure: drafts/vol{V}/{Type}_vol{V}_ch{N}/
        Example: drafts/vol2/Interlude_vol2_ch1/
        """
        dirname = f"{self.type.value}_vol{self.volume}_ch{self.number}"
        return drafts_root / f"vol{self.volume}" / dirname

    def sort_key(self) -> tuple[int, int, int]:
        """
        Sorting key for ordering chapters.
        Returns (volume, type_weight, number).
        Extras are sorted after all volume content (volume=9999).
        """
        if self.type == ChapterType.EXTRA:
            return (9999, _TYPE_SORT_ORDER[self.type], self.number)
        return (self.volume, _TYPE_SORT_ORDER[self.type], self.number)

    def display_name(self) -> str:
        """Human-readable display name."""
        if self.type == ChapterType.PROLOGUE:
            return f"Vol.{self.volume} Prologue"
        elif self.type == ChapterType.FINALE:
            return f"Vol.{self.volume} Finale"
        elif self.type == ChapterType.CHAPTER:
            return f"Vol.{self.volume} Chapter {self.number}"
        elif self.type == ChapterType.INTERLUDE:
            return f"Vol.{self.volume} Interlude {self.number}"
        elif self.type == ChapterType.EXTRA:
            return f"Extra {self.number}"
        return str(self)


# Filename parsing patterns
_PATTERNS: list[tuple[re.Pattern, ChapterType, bool]] = [
    # bool indicates whether the pattern captures a number group
    (re.compile(r"^Prologue\.md$"), ChapterType.PROLOGUE, False),
    (re.compile(r"^Finale\.md$"), ChapterType.FINALE, False),
    (re.compile(r"^Chapter\.(\d{3})\.md$"), ChapterType.CHAPTER, True),
    (re.compile(r"^Interlude\.(\d{3})\.md$"), ChapterType.INTERLUDE, True),
    (re.compile(r"^Extra\.(\d{3})\.md$"), ChapterType.EXTRA, True),
]

_DRAFT_DIR_PATTERN = re.compile(r"^(Prologue|Chapter|Interlude|Finale|Extra)_vol(\d+)_ch(\d+)$")


def parse_filename(filename: str, volume: int = 0) -> Optional[ChapterId]:
    """
    Parse a standardized filename into a ChapterId.

    Args:
        filename: The filename (e.g., "Chapter.001.md")
        volume: The volume number (inferred from directory context).
                Ignored for Extra type.

    Returns:
        ChapterId or None if the filename doesn't match any pattern.
    """
    for pattern, chapter_type, has_number in _PATTERNS:
        match = pattern.match(filename)
        if match:
            number = int(match.group(1)) if has_number else 0
            vol = 0 if chapter_type == ChapterType.EXTRA else volume
            return ChapterId(type=chapter_type, volume=vol, number=number)
    return None


def scan_chapters(chapters_root: Path) -> list[ChapterId]:
    """
    Scan the chapters directory and return all found chapter IDs, sorted.

    Args:
        chapters_root: The project's chapters/ directory.

    Returns:
        Sorted list of ChapterId objects.
    """
    results: list[ChapterId] = []

    if not chapters_root.exists():
        return results

    # Scan volume directories
    for vol_dir in sorted(chapters_root.iterdir()):
        if not vol_dir.is_dir():
            continue

        # Parse volume number from directory name
        vol_match = re.match(r"^vol(\d+)$", vol_dir.name)
        if vol_match:
            volume = int(vol_match.group(1))
            for md_file in vol_dir.glob("*.md"):
                chapter_id = parse_filename(md_file.name, volume=volume)
                if chapter_id:
                    results.append(chapter_id)

        # Scan extras directory
        elif vol_dir.name == "extras":
            for md_file in vol_dir.glob("*.md"):
                chapter_id = parse_filename(md_file.name, volume=0)
                if chapter_id:
                    results.append(chapter_id)

    results.sort(key=lambda c: c.sort_key())
    return results


def _scan_draft_dirs(drafts_root: Path, required_files: tuple[str, ...]) -> list[ChapterId]:
    results: list[ChapterId] = []

    if not drafts_root.exists():
        return results

    for vol_dir in sorted(drafts_root.iterdir()):
        if not vol_dir.is_dir():
            continue

        vol_match = re.match(r"^vol(\d+)$", vol_dir.name)
        if vol_match:
            volume = int(vol_match.group(1))
            for draft_dir in vol_dir.iterdir():
                if not draft_dir.is_dir():
                    continue
                match = _DRAFT_DIR_PATTERN.match(draft_dir.name)
                if not match:
                    continue
                type_str, _, num_str = match.groups()
                chapter_type = ChapterType(type_str)
                number = int(num_str)
                if any((draft_dir / filename).exists() for filename in required_files):
                    results.append(ChapterId(type=chapter_type, volume=volume, number=number))

    results.sort(key=lambda c: c.sort_key())
    return results


def scan_drafts(drafts_root: Path) -> list[ChapterId]:
    """
    Scan the drafts directory for nested draft folders that contain draft.md.

    Draft structure: drafts/vol{V}/{Type}_vol{V}_ch{N}/draft.md
    Example: drafts/vol2/Interlude_vol2_ch1/draft.md
    """
    return _scan_draft_dirs(drafts_root, ("draft.md",))



def scan_chapter_workspaces(drafts_root: Path) -> list[ChapterId]:
    """
    Scan the drafts directory for chapter workspaces.

    A workspace is recognized when the chapter directory exists and contains at
    least one of outline.md, concept.md, or draft.md.
    """
    return _scan_draft_dirs(drafts_root, DRAFT_WORKSPACE_FILENAMES)
