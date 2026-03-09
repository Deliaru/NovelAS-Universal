"""
Lore database management with Propose-Commit pattern.
Ported from NovelAS novel_mcp_server.py with enhancements:
- Git auto-commit on patch commit
- Standardized YAML frontmatter
- Full-text search
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from backend.core.project_manager import get_project_path
from backend.models.lore import (
    CommitResult,
    LoreEntry,
    LoreEntryDetail,
    LorePatchRequest,
    LoreSearchResult,
    LoreSnapshot,
    PatchReview,
)
from backend.models.patch import PendingPatch
from backend.utils.frontmatter import (
    LORE_FRONTMATTER_TEMPLATE,
    build_frontmatter,
    parse_frontmatter,
)
from backend.utils.git_ops import commit_changes
from backend.utils.logging_config import logger

# Valid lore categories
LORE_CATEGORIES = ["characters", "factions", "worldview", "items"]


def _lore_root(slug: str) -> Path:
    return get_project_path(slug) / "lore_database"


def _pending_patch_path(slug: str) -> Path:
    return get_project_path(slug) / ".pending_patch.json"


def get_snapshot(slug: str) -> LoreSnapshot:
    """Get a lightweight overview of all lore entries."""
    lore_dir = _lore_root(slug)
    entries = []

    for category in LORE_CATEGORIES:
        cat_dir = lore_dir / category
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                parsed = parse_frontmatter(content)
                name = parsed.metadata.get("name", md_file.stem)
                summary = parsed.body[:150].replace("\n", " ").strip()
                entry_id = f"{category}/{md_file.name}"
                entries.append(
                    LoreEntry(
                        id=entry_id,
                        name=name,
                        category=category,
                        summary=summary,
                        metadata=parsed.metadata,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read lore entry {md_file}: {e}")

    return LoreSnapshot(entries=entries, total=len(entries))


def get_entry_details(slug: str, entry_ids: list[str]) -> list[LoreEntryDetail]:
    """
    Get full details for specific lore entries.

    Args:
        entry_ids: List of entry IDs like ["characters/束.md", "worldview/理律.md"]
    """
    lore_dir = _lore_root(slug)
    results = []

    for entry_id in entry_ids:
        filepath = lore_dir / entry_id
        if not filepath.exists():
            continue
        try:
            content = filepath.read_text(encoding="utf-8")
            parsed = parse_frontmatter(content)
            category = entry_id.split("/")[0] if "/" in entry_id else "unknown"
            results.append(
                LoreEntryDetail(
                    id=entry_id,
                    name=parsed.metadata.get("name", filepath.stem),
                    category=category,
                    metadata=parsed.metadata,
                    content=parsed.body,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to read entry {entry_id}: {e}")

    return results


def search_lore(slug: str, keyword: str, category: str | None = None) -> list[LoreSearchResult]:
    """
    Full-text search across all lore entries.
    """
    lore_dir = _lore_root(slug)
    results = []
    keyword_lower = keyword.lower()

    categories = [category] if category else LORE_CATEGORIES

    for cat in categories:
        cat_dir = lore_dir / cat
        if not cat_dir.exists():
            continue
        for md_file in cat_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                content_lower = content.lower()
                if keyword_lower not in content_lower:
                    continue

                parsed = parse_frontmatter(content)
                # Extract excerpt around match
                idx = content_lower.find(keyword_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(keyword) + 50)
                excerpt = content[start:end].replace("\n", " ").strip()
                if start > 0:
                    excerpt = "..." + excerpt
                if end < len(content):
                    excerpt = excerpt + "..."

                results.append(
                    LoreSearchResult(
                        id=f"{cat}/{md_file.name}",
                        name=parsed.metadata.get("name", md_file.stem),
                        category=cat,
                        excerpt=excerpt,
                    )
                )
            except Exception as e:
                logger.warning(f"Search failed for {md_file}: {e}")

    return results


def propose_patch(slug: str, request: LorePatchRequest) -> PatchReview:
    """
    Stage a lore patch and generate a human-readable diff report.
    Saves the pending patch to .pending_patch.json in the project directory.
    """
    lore_dir = _lore_root(slug)
    patch_id = uuid.uuid4().hex[:8]

    # Generate diff report
    diff_lines = [f"## Lore Patch #{patch_id}\n"]

    for update in request.lore_updates:
        category = update.category
        if category in ("character",):
            category = "characters"

        filepath = lore_dir / category / f"{update.name}.md"
        if filepath.exists():
            diff_lines.append(f"### UPDATE: {category}/{update.name}.md")
            old_content = filepath.read_text(encoding="utf-8")
            old_parsed = parse_frontmatter(old_content)
            diff_lines.append(f"  - Existing: {len(old_parsed.body)} chars")
            diff_lines.append(f"  - New content: {len(update.content)} chars")
            if update.metadata:
                diff_lines.append(f"  - Metadata changes: {list(update.metadata.keys())}")
        else:
            diff_lines.append(f"### NEW: {category}/{update.name}.md")
            diff_lines.append(f"  - Content: {len(update.content)} chars")
            if update.metadata:
                diff_lines.append(f"  - Metadata: {list(update.metadata.keys())}")

        diff_lines.append("")

    # Save pending patch
    pending = PendingPatch(
        patch_id=patch_id,
        lore_updates=[u.model_dump() for u in request.lore_updates],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    patch_path = _pending_patch_path(slug)
    patch_path.write_text(
        json.dumps(pending.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    diff_text = "\n".join(diff_lines)
    logger.info(f"Proposed patch {patch_id} with {len(request.lore_updates)} updates")
    return PatchReview(
        patch_id=patch_id,
        diff_text=diff_text,
        update_count=len(request.lore_updates),
    )


def commit_patch(slug: str, patch_id: str) -> CommitResult:
    """
    Apply a pending patch. Writes files and auto-commits to Git.

    Raises:
        FileNotFoundError: If no pending patch exists.
        ValueError: If patch_id doesn't match.
    """
    patch_path = _pending_patch_path(slug)
    if not patch_path.exists():
        raise FileNotFoundError("No pending patch found")

    pending_data = json.loads(patch_path.read_text(encoding="utf-8"))
    pending = PendingPatch(**pending_data)

    if pending.patch_id != patch_id:
        raise ValueError(f"Patch ID mismatch: expected {pending.patch_id}, got {patch_id}")

    lore_dir = _lore_root(slug)
    project_path = get_project_path(slug)
    updated_files = []

    for update in pending.lore_updates:
        category = update.get("category", "")
        if category in ("character",):
            category = "characters"
        name = update.get("name", "")
        content = update.get("content", "")
        metadata = update.get("metadata", {})
        source = update.get("source", "")
        update_type = update.get("type", "update")

        # Ensure category directory exists
        cat_dir = lore_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        filepath = cat_dir / f"{name}.md"
        rel_path = str(filepath.relative_to(project_path))

        # Build standardized frontmatter
        fm = dict(LORE_FRONTMATTER_TEMPLATE)
        fm["name"] = name
        fm["category"] = category
        fm["last_updated"] = source or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if filepath.exists() and update_type == "update":
            # Merge with existing metadata
            existing = parse_frontmatter(filepath.read_text(encoding="utf-8"))
            for k, v in existing.metadata.items():
                if k not in fm or not fm[k]:
                    fm[k] = v
            # Append new content
            body = existing.body.rstrip("\n") + "\n\n" + content
        else:
            fm["first_appearance"] = source
            body = content

        # Apply user-provided metadata overrides
        for k, v in metadata.items():
            fm[k] = v

        full_content = build_frontmatter(fm, body)
        filepath.write_text(full_content, encoding="utf-8")
        updated_files.append(rel_path)

    # Remove pending patch
    patch_path.unlink()

    # Git commit
    git_sha = commit_changes(
        project_path,
        updated_files,
        f"Lore patch #{patch_id}: updated {len(updated_files)} entries",
    )

    logger.info(f"Committed patch {patch_id}: {len(updated_files)} files")
    return CommitResult(updated_files=updated_files, git_sha=git_sha)


def reject_patch(slug: str, patch_id: str) -> None:
    """Discard a pending patch."""
    patch_path = _pending_patch_path(slug)
    if patch_path.exists():
        patch_path.unlink()
        logger.info(f"Rejected patch {patch_id}")


def update_lore_entry(
    slug: str,
    category: str,
    name: str,
    content: str,
    metadata: dict | None = None,
) -> str:
    """
    Direct update of a lore entry (bypasses Propose-Commit for GUI edits).
    Auto-commits to Git.
    """
    lore_dir = _lore_root(slug)
    project_path = get_project_path(slug)

    cat_dir = lore_dir / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    filepath = cat_dir / f"{name}.md"

    fm = dict(LORE_FRONTMATTER_TEMPLATE)
    fm["name"] = name
    fm["category"] = category
    fm["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if filepath.exists():
        existing = parse_frontmatter(filepath.read_text(encoding="utf-8"))
        for k, v in existing.metadata.items():
            if k not in fm or not fm[k]:
                fm[k] = v

    if metadata:
        for k, v in metadata.items():
            fm[k] = v

    full_content = build_frontmatter(fm, content)
    filepath.write_text(full_content, encoding="utf-8")

    rel_path = str(filepath.relative_to(project_path))
    commit_changes(project_path, [rel_path], f"Update lore: {category}/{name}")

    return rel_path


def get_index_files(slug: str) -> list[LoreEntry]:
    """
    Get all files from the lore_database/index directory.
    These are typically index/reference files like character lists, timelines, etc.
    """
    lore_dir = _lore_root(slug)
    index_dir = lore_dir / "index"
    entries = []

    if not index_dir.exists():
        return entries

    for md_file in sorted(index_dir.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
            parsed = parse_frontmatter(content)
            name = parsed.metadata.get("name", md_file.stem)
            summary = parsed.body[:150].replace("\n", " ").strip()
            entry_id = f"index/{md_file.name}"
            entries.append(
                LoreEntry(
                    id=entry_id,
                    name=name,
                    category="index",
                    summary=summary,
                    metadata=parsed.metadata,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to read index file {md_file}: {e}")

    return entries
