"""
Data importer from the original NovelAS project.
Handles migration of chapters, lore, knowledge, and seed data
with proper filename translation and format standardization.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Optional

import yaml

from backend.core.naming import ChapterId, ChapterType
from backend.core.project_manager import create_project, get_project_path
from backend.models.project import CreateProjectRequest, ProjectSettings, VolumeConfig
from backend.utils.frontmatter import (
    LORE_FRONTMATTER_TEMPLATE,
    build_frontmatter,
    parse_frontmatter,
)
from backend.utils.git_ops import commit_changes, init_repo
from backend.utils.logging_config import logger


# Mapping from old-format filenames to new ChapterIds
def _map_old_chapter(filename: str, volume: int) -> Optional[ChapterId]:
    """
    Map old NovelAS chapter filenames to new ChapterId.

    Old format:
        ch000.md          → Prologue (if from Prologue source) or Chapter.000
        ch001.md-ch035.md → Chapter.001-Chapter.035
        interlude_01.md   → Interlude.000 (1-based to 0-based)
        interlude_100.md  → Extra.000 (BUG FIX: was actually Extra.0)
        extra_01.md       → Extra.001
        finale.md         → Finale
    """
    # finale.md
    if filename.lower().startswith("finale"):
        return ChapterId(type=ChapterType.FINALE, volume=volume, number=0)

    # interlude_100.md → This is the bug: it's actually Extra.0
    match = re.match(r"interlude_100\.md$", filename)
    if match:
        return ChapterId(type=ChapterType.EXTRA, volume=0, number=0)

    # extra_NN.md → Extra.NNN (keep the number)
    match = re.match(r"extra_(\d+)\.md$", filename)
    if match:
        num = int(match.group(1))
        return ChapterId(type=ChapterType.EXTRA, volume=0, number=num)

    # interlude_NN.md → Interlude.NNN (convert from 1-based to 0-based)
    match = re.match(r"interlude_(\d+)\.md$", filename)
    if match:
        num = int(match.group(1))
        return ChapterId(type=ChapterType.INTERLUDE, volume=volume, number=num - 1)

    # ch000.md → Prologue (heuristic: check if content mentions prologue/序章)
    match = re.match(r"ch000\.md$", filename)
    if match:
        return ChapterId(type=ChapterType.PROLOGUE, volume=volume, number=0)

    # chNNN.md → Chapter.NNN
    match = re.match(r"ch(\d{3})\.md$", filename)
    if match:
        num = int(match.group(1))
        if num == 0:
            return ChapterId(type=ChapterType.PROLOGUE, volume=volume, number=0)
        return ChapterId(type=ChapterType.CHAPTER, volume=volume, number=num)

    return None


def _standardize_lore_frontmatter(
    content: str, category: str, filename: str
) -> str:
    """
    Standardize a lore file's YAML frontmatter to the new template.
    Preserves existing metadata and fills in missing fields.
    """
    parsed = parse_frontmatter(content)
    metadata = {**LORE_FRONTMATTER_TEMPLATE}

    # Merge existing metadata
    for key, value in parsed.metadata.items():
        metadata[key] = value

    # Ensure required fields
    if not metadata.get("name"):
        metadata["name"] = Path(filename).stem
    if not metadata.get("category"):
        metadata["category"] = category

    return build_frontmatter(metadata, parsed.body)


def import_from_novelas(
    source_dir: str | Path,
    project_name: str,
    project_slug: str,
    description: str = "",
) -> dict:
    """
    Import data from an existing NovelAS project into a new Universal project.

    Args:
        source_dir: Path to the original NovelAS project (e.g., D:\\Work\\NovelAS)
        project_name: Display name for the new project
        project_slug: URL-safe slug for the new project
        description: Project description

    Returns:
        Summary dict with counts of imported items.
    """
    source = Path(source_dir)
    if not source.exists():
        raise FileNotFoundError(f"Source directory not found: {source}")

    stats = {
        "chapters": 0,
        "lore_entries": 0,
        "knowledge_files": 0,
        "seed_files": 0,
        "errors": [],
    }

    # Detect volumes
    volumes = []
    processed_dir = source / "processed_chapters"
    if processed_dir.exists():
        for vol_dir in sorted(processed_dir.iterdir()):
            if vol_dir.is_dir():
                match = re.match(r"vol(\d+)", vol_dir.name)
                if match:
                    vol_num = int(match.group(1))
                    volumes.append(
                        VolumeConfig(
                            number=vol_num,
                            title=f"第{_num_to_cn(vol_num)}卷",
                            source_dir=f"source/vol{vol_num}",
                        )
                    )

    if not volumes:
        volumes = [VolumeConfig(number=1, title="第一卷")]

    # Create project
    request = CreateProjectRequest(
        name=project_name,
        slug=project_slug,
        description=description,
        volumes=volumes,
        settings=ProjectSettings(language="zh-CN"),
    )
    create_project(request)
    project_path = get_project_path(project_slug)
    chapters_root = project_path / "chapters"

    # --- Import chapters ---
    logger.info("Importing chapters...")
    extra_counter = 0  # Track global Extra numbering

    for vol_dir in sorted(processed_dir.iterdir()):
        if not vol_dir.is_dir():
            continue
        match = re.match(r"vol(\d+)", vol_dir.name)
        if not match:
            continue
        volume = int(match.group(1))

        for md_file in sorted(vol_dir.glob("*.md")):
            try:
                chapter_id = _map_old_chapter(md_file.name, volume)
                if chapter_id is None:
                    stats["errors"].append(f"Skipped unrecognized: {md_file.name}")
                    continue

                # Read content
                content = md_file.read_text(encoding="utf-8")

                # Write to new location
                output_path = chapter_id.to_path(chapters_root)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content, encoding="utf-8")
                stats["chapters"] += 1

            except Exception as e:
                stats["errors"].append(f"Failed to import {md_file.name}: {e}")

    # --- Import lore database ---
    logger.info("Importing lore database...")
    lore_source = source / "lore_database"
    lore_target = project_path / "lore_database"

    if lore_source.exists():
        for category_dir in sorted(lore_source.iterdir()):
            if not category_dir.is_dir():
                continue

            # Merge 'character' (singular) into 'characters' (plural)
            target_name = category_dir.name
            if target_name == "character":
                target_name = "characters"

            # Skip 'imports' directory (raw migration artifacts)
            if target_name == "imports":
                continue

            target_dir = lore_target / target_name
            target_dir.mkdir(parents=True, exist_ok=True)

            for md_file in category_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    standardized = _standardize_lore_frontmatter(
                        content, target_name, md_file.name
                    )
                    (target_dir / md_file.name).write_text(
                        standardized, encoding="utf-8"
                    )
                    stats["lore_entries"] += 1
                except Exception as e:
                    stats["errors"].append(f"Lore import failed {md_file.name}: {e}")

    # --- Import knowledge ---
    logger.info("Importing knowledge files...")
    knowledge_source = source / ".gemini" / "knowledge"
    if knowledge_source.exists():
        # Project-specific guides
        guides_src = knowledge_source / "project_guides"
        if guides_src.exists():
            guides_dst = project_path / "knowledge"
            guides_dst.mkdir(parents=True, exist_ok=True)
            for f in guides_src.glob("*.md"):
                try:
                    shutil.copy2(f, guides_dst / f.name)
                    stats["knowledge_files"] += 1
                except Exception as e:
                    stats["errors"].append(f"Knowledge import failed {f.name}: {e}")

    # --- Import seed data ---
    logger.info("Importing seed data...")
    seed_file = source / "空理之典.json"
    if seed_file.exists():
        try:
            seed_dst = project_path / "seed" / seed_file.name
            shutil.copy2(seed_file, seed_dst)
            stats["seed_files"] += 1
        except Exception as e:
            stats["errors"].append(f"Seed import failed: {e}")

    # --- Copy source DOCX files (optional) ---
    novel_dir = source / "Novel"
    if novel_dir.exists():
        for vol_name in sorted(novel_dir.iterdir()):
            if not vol_name.is_dir():
                continue
            vol_num_match = re.search(r"(\d+)", vol_name.name)
            # Use Chinese number detection
            cn_match = re.search(r"第([\u4e00-\u9fff])卷", vol_name.name)
            if cn_match:
                cn_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
                vol_num = cn_map.get(cn_match.group(1), 1)
            elif vol_num_match:
                vol_num = int(vol_num_match.group(1))
            else:
                continue

            src_dst = project_path / "source" / f"vol{vol_num}"
            src_dst.mkdir(parents=True, exist_ok=True)
            for docx in vol_name.glob("*.docx"):
                shutil.copy2(docx, src_dst / docx.name)

    # --- Git initial commit ---
    try:
        lore_files = [
            str(f.relative_to(project_path))
            for f in (project_path / "lore_database").rglob("*.md")
        ]
        if lore_files:
            commit_changes(
                project_path,
                lore_files + ["project.yaml"],
                "Import from NovelAS: initial lore data",
            )
    except Exception as e:
        logger.warning(f"Git commit after import failed: {e}")

    logger.info(f"Import complete: {stats}")
    return stats


def _num_to_cn(n: int) -> str:
    """Convert a small integer to Chinese numeral."""
    cn = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
          6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
    return cn.get(n, str(n))
