"""
DOCX to Markdown converter with standardized chapter naming.

Rewrites the original NovelAS converter to:
1. Fix the Extra.0 → interlude_100 bug (original line 144: < -100 should be <= -100)
2. Use ChapterId type system instead of negative number encoding
3. Support configurable volume mapping from project.yaml
4. Improve heading detection heuristics
"""

import re
from pathlib import Path
from typing import Optional

from docx import Document

from backend.core.naming import ChapterId, ChapterType
from backend.utils.frontmatter import build_frontmatter
from backend.utils.logging_config import logger


class DocxConverter:
    """Converts DOCX novel chapters to standardized Markdown files."""

    def __init__(self, project_root: Path, volume_map: dict[str, int] | None = None):
        """
        Args:
            project_root: Project directory (contains source/ and chapters/).
            volume_map: Maps directory names to volume numbers.
                        e.g., {"第一卷": 1, "第二卷": 2}
                        If None, auto-detects from directory names.
        """
        self.project_root = project_root
        self.source_dir = project_root / "source"
        self.chapters_dir = project_root / "chapters"
        self.volume_map = volume_map or {}

    def _detect_volume(self, dir_name: str) -> int:
        """
        Detect volume number from a directory name.
        Supports: vol1, 第一卷, Volume 1, etc.
        """
        if dir_name in self.volume_map:
            return self.volume_map[dir_name]

        # Try volN pattern
        match = re.match(r"vol(\d+)", dir_name, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Try Chinese volume names
        cn_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        match = re.search(r"第([\u4e00-\u9fff])卷", dir_name)
        if match:
            return cn_map.get(match.group(1), 1)

        # Try digit in name
        match = re.search(r"(\d+)", dir_name)
        if match:
            return int(match.group(1))

        return 1  # Default

    def parse_source_filename(self, filename: str, volume: int) -> Optional[ChapterId]:
        """
        Parse a source DOCX filename into a ChapterId.

        Supported patterns:
            Chapter.{N}.docx           → Chapter in current volume
            Chapter.{V}-{N}.docx       → Chapter in volume V
            Interlude.{N}.docx         → Interlude in current volume
            Interlude.{V}-{N}.docx     → Interlude in volume V
            Extra.{N}.docx             → Extra (global numbering)
            Extra.{N} {title}.docx     → Extra with title
            A.Prologue.{N}.docx        → Prologue
            Prologue...                → Prologue
            Finale.{N}.docx            → Finale
        """
        basename = filename.replace(".docx", "").replace(".DOCX", "")

        # Chapter.{V}-{N} (volume-specific)
        match = re.match(r"Chapter\.(\d+)-(\d+)", basename)
        if match:
            vol = int(match.group(1))
            num = int(match.group(2))
            return ChapterId(type=ChapterType.CHAPTER, volume=vol, number=num)

        # Chapter.{N} (current volume)
        match = re.match(r"Chapter\.(\d+)$", basename)
        if match:
            num = int(match.group(1))
            return ChapterId(type=ChapterType.CHAPTER, volume=volume, number=num)

        # Interlude.{V}-{N} (volume-specific)
        match = re.match(r"Interlude\.(\d+)-(\d+)", basename)
        if match:
            vol = int(match.group(1))
            num = int(match.group(2))
            return ChapterId(type=ChapterType.INTERLUDE, volume=vol, number=num)

        # Interlude.{N} (current volume)
        match = re.match(r"Interlude\.(\d+)", basename)
        if match:
            num = int(match.group(1))
            return ChapterId(type=ChapterType.INTERLUDE, volume=volume, number=num)

        # Extra.{N} (global numbering) - may have title after number
        match = re.match(r"Extra\.(\d+)", basename)
        if match:
            num = int(match.group(1))
            return ChapterId(type=ChapterType.EXTRA, volume=0, number=num)

        # Prologue
        if "Prologue" in basename or "prologue" in basename:
            return ChapterId(type=ChapterType.PROLOGUE, volume=volume, number=0)

        # Finale
        match = re.match(r"Finale\.(\d+)", basename)
        if match:
            return ChapterId(type=ChapterType.FINALE, volume=volume, number=0)
        if "Finale" in basename or "finale" in basename:
            return ChapterId(type=ChapterType.FINALE, volume=volume, number=0)

        return None

    def extract_text(self, docx_path: Path) -> str:
        """
        Extract text from a DOCX file, converting to Markdown.
        Improved heading detection over the original.
        """
        try:
            doc = Document(docx_path)
        except Exception as e:
            logger.error(f"Failed to read DOCX: {docx_path}: {e}")
            return ""

        lines: list[str] = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Detect headings using Word styles first
            if para.style and para.style.name and "Heading" in para.style.name:
                level = 2
                match = re.search(r"(\d+)", para.style.name)
                if match:
                    level = min(int(match.group(1)) + 1, 4)
                lines.append(f"\n{'#' * level} {text}\n")
                continue

            # Heuristic heading detection:
            # Short text without sentence-ending punctuation
            is_short = len(text) < 40
            no_end_punct = text[-1] not in "。！？…」』）)\"'"
            no_mid_punct = not any(p in text for p in "，、；：")
            if is_short and no_end_punct and no_mid_punct:
                lines.append(f"\n## {text}\n")
            else:
                lines.append(text)

        return "\n\n".join(lines)

    def convert_file(self, docx_path: Path, volume: int) -> Optional[Path]:
        """
        Convert a single DOCX file to Markdown.

        Returns the output path, or None if conversion failed.
        """
        chapter_id = self.parse_source_filename(docx_path.name, volume)
        if chapter_id is None:
            logger.warning(f"Skipping unrecognized file: {docx_path.name}")
            return None

        content = self.extract_text(docx_path)
        if not content:
            return None

        # Build output path
        output_path = chapter_id.to_path(self.chapters_dir)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build document with frontmatter
        metadata = {
            "title": chapter_id.display_name(),
            "type": chapter_id.type.value,
            "volume": chapter_id.volume,
            "number": chapter_id.number,
            "source_file": docx_path.name,
        }
        full_content = build_frontmatter(metadata, content)

        output_path.write_text(full_content, encoding="utf-8")
        logger.info(f"Converted: {docx_path.name} -> {output_path.relative_to(self.project_root)}")
        return output_path

    def convert_volume(self, volume_dir: Path) -> list[Path]:
        """Convert all DOCX files in a volume directory."""
        if not volume_dir.exists():
            logger.error(f"Volume directory not found: {volume_dir}")
            return []

        volume = self._detect_volume(volume_dir.name)
        docx_files = sorted(volume_dir.glob("*.docx")) + sorted(volume_dir.glob("*.DOCX"))
        results = []

        logger.info(f"Converting {len(docx_files)} files from {volume_dir.name} (vol {volume})")

        for docx_file in docx_files:
            output = self.convert_file(docx_file, volume)
            if output:
                results.append(output)

        logger.info(f"Converted {len(results)}/{len(docx_files)} files from {volume_dir.name}")
        return results

    def convert_all(self) -> list[Path]:
        """Convert all volumes found in the source directory."""
        if not self.source_dir.exists():
            logger.error(f"Source directory not found: {self.source_dir}")
            return []

        all_results: list[Path] = []
        for entry in sorted(self.source_dir.iterdir()):
            if entry.is_dir():
                all_results.extend(self.convert_volume(entry))

        logger.info(f"Total converted: {len(all_results)} files")
        return all_results
