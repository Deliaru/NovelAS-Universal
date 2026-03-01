"""
MCP Server wrapper - thin FastMCP layer delegating to core/ managers.
Provides backward-compatible tool interface for Gemini CLI and Claude Code.

Usage:
    python -m backend.mcp.server
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

from backend.core import chapter_manager, job_manager, knowledge_manager, lore_manager
from backend.core.naming import ChapterId, ChapterType
from backend.models.lore import LorePatchRequest, LorePatchUpdate
from backend.services import vector_memory

mcp = FastMCP("NovelAS Universal")

# Default project slug (set via environment or first project found)
import os
DEFAULT_SLUG = os.environ.get("NOVELAS_PROJECT", "")


def _get_slug() -> str:
    """Get the active project slug."""
    if DEFAULT_SLUG:
        return DEFAULT_SLUG
    # Try to find first project
    from backend.config import settings
    projects_dir = settings.get_projects_dir()
    if projects_dir.exists():
        for entry in projects_dir.iterdir():
            if entry.is_dir() and (entry / "project.yaml").exists():
                return entry.name
    raise RuntimeError("No project configured. Set NOVELAS_PROJECT env var.")


@mcp.tool()
def read_chapter_content(volume: int, chapter: int, chapter_type: str = "Chapter") -> str:
    """Read the full content of a chapter."""
    slug = _get_slug()
    ct = ChapterType(chapter_type)
    cid = ChapterId(type=ct, volume=volume, number=chapter)
    result = chapter_manager.read_chapter_content(slug, cid)
    return result.content


@mcp.tool()
def list_chapters(volume: int = 0) -> str:
    """List all chapters in a volume."""
    slug = _get_slug()
    vol = volume if volume > 0 else None
    chapters = chapter_manager.list_chapters(slug, volume=vol)
    return json.dumps([c.model_dump() for c in chapters], ensure_ascii=False, indent=2)


@mcp.tool()
def get_lore_snapshot() -> str:
    """Get a lightweight overview of all lore entries."""
    slug = _get_slug()
    snapshot = lore_manager.get_snapshot(slug)
    return json.dumps([e.model_dump() for e in snapshot.entries], ensure_ascii=False, indent=2)


@mcp.tool()
def get_entry_details(entry_ids: str) -> str:
    """Get full details for specific lore entries. entry_ids is comma-separated."""
    slug = _get_slug()
    ids = [i.strip() for i in entry_ids.split(",")]
    details = lore_manager.get_entry_details(slug, ids)
    return json.dumps([d.model_dump() for d in details], ensure_ascii=False, indent=2)


@mcp.tool()
def search_lore(keyword: str, category: str = "") -> str:
    """Search lore database by keyword."""
    slug = _get_slug()
    cat = category if category else None
    results = lore_manager.search_lore(slug, keyword, cat)
    return json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2)


@mcp.tool()
def propose_patch(patch_json: str) -> str:
    """Propose a lore patch. Input is JSON with lore_updates array."""
    slug = _get_slug()
    data = json.loads(patch_json)
    request = LorePatchRequest(
        lore_updates=[LorePatchUpdate(**u) for u in data.get("lore_updates", [])]
    )
    review = lore_manager.propose_patch(slug, request)
    return review.diff_text


@mcp.tool()
def commit_patch(confirmation: str) -> str:
    """Commit a pending lore patch. Pass the patch_id as confirmation."""
    slug = _get_slug()
    result = lore_manager.commit_patch(slug, confirmation)
    return json.dumps(result.model_dump(), ensure_ascii=False)


@mcp.tool()
def save_chapter_draft(volume: int, chapter: int, content: str) -> str:
    """Save a chapter draft."""
    slug = _get_slug()
    cid = ChapterId(type=ChapterType.CHAPTER, volume=volume, number=chapter)
    path = chapter_manager.save_chapter_draft(slug, cid, content)
    return f"Draft saved: {path}"


@mcp.tool()
def query_plot_memory(query: str, n_results: int = 5) -> str:
    """Query the vector memory database for similar plot points."""
    slug = _get_slug()
    results = vector_memory.query_memory(slug, query, top_k=n_results)
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def store_plot_memory(content: str, metadata_json: str) -> str:
    """Store a plot memory entry. metadata_json should include volume, chapter, type."""
    slug = _get_slug()
    metadata = json.loads(metadata_json)
    memory_id = vector_memory.store_memory(slug, content, metadata)
    return f"Stored: {memory_id}"


@mcp.tool()
def calculate_chapter_batches(
    volume: int, max_chars: int = 50000,
    start_chapter: int = -1, end_chapter: int = -1
) -> str:
    """Calculate chapter batches for a volume."""
    slug = _get_slug()
    start = start_chapter if start_chapter >= 0 else None
    end = end_chapter if end_chapter >= 0 else None
    result = job_manager.calculate_batches(slug, volume, max_chars, start, end)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


@mcp.tool()
def claim_next_batch(job_id: str) -> str:
    """Claim the next batch in a job."""
    result = job_manager.claim_next_batch(job_id)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


@mcp.tool()
def update_knowledge_file(filename: str, content: str, subdir: str = "") -> str:
    """Update or create a knowledge file."""
    slug = _get_slug()
    path = f"{subdir}/{filename}" if subdir else filename
    filepath = knowledge_manager.update_knowledge_file(path, content, slug=slug)
    return f"Saved: {filepath}"


if __name__ == "__main__":
    mcp.run()
