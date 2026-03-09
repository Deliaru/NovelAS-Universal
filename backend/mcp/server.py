"""
MCP Server wrapper - thin FastMCP layer delegating to core/ managers.
Provides backward-compatible tool interface for Gemini CLI and Claude Code.

Usage:
    python -m backend.mcp.server
"""

import json
import sys
import os
import threading
import functools
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

from backend.core import chapter_manager, job_manager, knowledge_manager, lore_manager
from backend.core.naming import ChapterId, ChapterType
from backend.models.lore import LorePatchRequest, LorePatchUpdate
from backend.services import vector_memory

mcp = FastMCP("NovelAS Universal")


class ToolTimeoutError(Exception):
    """Raised when a tool execution times out."""
    pass


def with_tool_timeout(seconds: int):
    """
    Decorator to add timeout to MCP tool functions.
    Returns a helpful error message with retry instructions.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import logging
            logger = logging.getLogger("novelas")

            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                error_msg = (
                    f"⚠️ Tool '{func.__name__}' timed out after {seconds} seconds.\n\n"
                    f"This may be due to:\n"
                    f"1. First-time model loading (vector memory tools)\n"
                    f"2. Heavy system load\n"
                    f"3. Resource contention\n\n"
                    f"🔄 RECOMMENDED ACTION: Retry this exact same call.\n"
                    f"   Most timeouts resolve on retry (cached resources).\n\n"
                    f"If the problem persists after 2-3 retries:\n"
                    f"- Check system resources (CPU, memory)\n"
                    f"- Review logs: novelas.log\n"
                    f"- Try the 'ping' tool to test connectivity"
                )
                logger.error(f"{func.__name__} timed out after {seconds}s with args={args}, kwargs={kwargs}")
                sys.stdout.flush()
                return error_msg

            if exception[0]:
                logger.error(f"{func.__name__} raised exception: {exception[0]}", exc_info=True)
                sys.stdout.flush()
                return f"Error in {func.__name__}: {type(exception[0]).__name__}: {exception[0]}"

            return result[0]
        return wrapper
    return decorator


def _warmup_services():
    """Pre-initialize services to avoid first-call delays."""
    import logging
    logger = logging.getLogger("novelas")

    try:
        logger.info("Warming up vector memory service...")
        # Trigger lazy initialization
        from backend.services import vector_memory
        vector_memory._get_chroma()
        logger.info("Vector memory service warmed up successfully")
    except Exception as e:
        logger.warning(f"Warmup failed (non-critical): {e}")


@mcp.tool()
def ping() -> str:
    """Simple ping tool to test MCP connectivity."""
    import time
    import os
    return json.dumps({
        "status": "ok",
        "message": "MCP server is responsive",
        "timestamp": time.time(),
        "pid": os.getpid()
    }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def read_chapter_content(slug: str, volume: int, chapter: int, chapter_type: str = "Chapter") -> str:
    """
    Read the full content of a chapter.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        ct = ChapterType(chapter_type)
        cid = ChapterId(type=ct, volume=volume, number=chapter)
        logger.info(f"Reading chapter: {slug} {cid}")
        result = chapter_manager.read_chapter_content(slug, cid)
        logger.info(f"Chapter read successfully, length: {len(result.content)}")
        sys.stdout.flush()
        return result.content
    except Exception as e:
        logger.error(f"read_chapter_content error: {e}", exc_info=True)
        sys.stdout.flush()
        return f"Error reading chapter: {type(e).__name__}: {e}\n\n🔄 You can retry this call."


@mcp.tool()
@with_tool_timeout(10)
def list_chapters(slug: str, volume: int = 0) -> str:
    """
    List all chapters in a volume.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        vol = volume if volume > 0 else None
        logger.info(f"Listing chapters: {slug}, volume={vol}")
        chapters = chapter_manager.list_chapters(slug, volume=vol)
        result = json.dumps([c.model_dump() for c in chapters], ensure_ascii=False, indent=2)
        logger.info(f"Listed {len(chapters)} chapters")
        sys.stdout.flush()
        return result
    except Exception as e:
        logger.error(f"list_chapters error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def get_lore_snapshot(slug: str) -> str:
    """
    Get a lightweight overview of all lore entries.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        logger.info(f"Getting lore snapshot: {slug}")
        snapshot = lore_manager.get_snapshot(slug)
        result = json.dumps([e.model_dump() for e in snapshot.entries], ensure_ascii=False, indent=2)
        logger.info(f"Lore snapshot retrieved: {len(snapshot.entries)} entries")
        sys.stdout.flush()
        return result
    except Exception as e:
        logger.error(f"get_lore_snapshot error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def get_entry_details(slug: str, entry_ids: str) -> str:
    """
    Get full details for specific lore entries. entry_ids is comma-separated.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        ids = [i.strip() for i in entry_ids.split(",")]
        logger.info(f"Getting entry details: {slug}, ids={ids}")
        details = lore_manager.get_entry_details(slug, ids)
        result = json.dumps([d.model_dump() for d in details], ensure_ascii=False, indent=2)
        logger.info(f"Entry details retrieved: {len(details)} entries")
        sys.stdout.flush()
        return result
    except Exception as e:
        logger.error(f"get_entry_details error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def search_lore(slug: str, keyword: str, category: str = "") -> str:
    """
    Search lore database by keyword.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        cat = category if category else None
        logger.info(f"Searching lore: {slug}, keyword={keyword}, category={cat}")
        results = lore_manager.search_lore(slug, keyword, cat)
        result = json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2)
        logger.info(f"Lore search completed: {len(results)} results")
        sys.stdout.flush()
        return result
    except Exception as e:
        logger.error(f"search_lore error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(15)
def propose_patch(slug: str, patch_json: str) -> str:
    """
    Propose a lore patch. Input is JSON with lore_updates array.

    Timeout: 15 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        data = json.loads(patch_json)
        request = LorePatchRequest(
            lore_updates=[LorePatchUpdate(**u) for u in data.get("lore_updates", [])]
        )
        logger.info(f"Proposing patch: {slug}, {len(request.lore_updates)} updates")
        review = lore_manager.propose_patch(slug, request)
        logger.info(f"Patch proposed successfully")
        sys.stdout.flush()
        return review.diff_text
    except Exception as e:
        logger.error(f"propose_patch error: {e}", exc_info=True)
        sys.stdout.flush()
        return f"Error proposing patch: {type(e).__name__}: {e}\n\n🔄 You can retry this call."


@mcp.tool()
@with_tool_timeout(10)
def commit_patch(slug: str, confirmation: str) -> str:
    """
    Commit a pending lore patch. Pass the patch_id as confirmation.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        logger.info(f"Committing patch: {slug}, confirmation={confirmation}")
        result = lore_manager.commit_patch(slug, confirmation)
        logger.info(f"Patch committed successfully")
        sys.stdout.flush()
        return json.dumps(result.model_dump(), ensure_ascii=False)
    except Exception as e:
        logger.error(f"commit_patch error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def save_chapter_draft(slug: str, volume: int, chapter: int, content: str) -> str:
    """
    Save a chapter draft.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        cid = ChapterId(type=ChapterType.CHAPTER, volume=volume, number=chapter)
        logger.info(f"Saving chapter draft: {slug} {cid}")
        path = chapter_manager.save_chapter_draft(slug, cid, content)
        logger.info(f"Chapter draft saved: {path}")
        sys.stdout.flush()
        return f"Draft saved: {path}"
    except Exception as e:
        logger.error(f"save_chapter_draft error: {e}", exc_info=True)
        sys.stdout.flush()
        return f"Error saving draft: {type(e).__name__}: {e}\n\n🔄 You can retry this call."


@mcp.tool()
@with_tool_timeout(45)
def query_plot_memory(slug: str, query: str, n_results: int = 5) -> str:
    """
    Query the vector memory database for similar plot points.

    Timeout: 45 seconds (longer due to model loading on first call)
    If timeout occurs on first call, retry - model will be cached.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        logger.info(f"Querying plot memory: {slug}, query={query[:50]}..., n_results={n_results}")
        results = vector_memory.query_memory(slug, query, top_k=n_results)
        logger.info(f"Plot memory query completed: {len(results)} results")
        sys.stdout.flush()
        return json.dumps(results, ensure_ascii=False, indent=2)
    except TimeoutError as e:
        logger.error(f"query_plot_memory timeout: {e}")
        sys.stdout.flush()
        return json.dumps({
            "error": "timeout",
            "message": str(e),
            "hint": "🔄 RETRY THIS CALL - Vector memory service may be initializing (first call takes ~20s, subsequent calls <1s)"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"query_plot_memory error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": type(e).__name__,
            "message": str(e),
            "hint": "🔄 You can retry this call"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(90)
def store_plot_memory(slug: str, content: str, metadata_json: str) -> str:
    """
    Store a plot memory entry. metadata_json should include volume, chapter, type.

    Timeout: 90 seconds (longer due to model loading on first call)
    If timeout occurs on first call, retry - model will be cached.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        metadata = json.loads(metadata_json)
        logger.info(f"Storing plot memory: {slug}, content_length={len(content)}")
        memory_id = vector_memory.store_memory(slug, content, metadata)
        logger.info(f"Plot memory stored: {memory_id}")
        sys.stdout.flush()
        return f"Stored: {memory_id}"
    except Exception as e:
        logger.error(f"store_plot_memory error: {e}", exc_info=True)
        sys.stdout.flush()
        return f"Error: {type(e).__name__}: {e}\n\n🔄 RETRY if this was the first call (model loading)"


@mcp.tool()
@with_tool_timeout(15)
def calculate_chapter_batches(
    slug: str, volume: int, max_chars: int = 50000,
    start_chapter: int = -1, end_chapter: int = -1
) -> str:
    """
    Calculate chapter batches for a volume.

    Timeout: 15 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        start = start_chapter if start_chapter >= 0 else None
        end = end_chapter if end_chapter >= 0 else None
        logger.info(f"Calculating batches: {slug}, vol={volume}, max_chars={max_chars}")
        result = job_manager.calculate_batches(slug, volume, max_chars, start, end)
        logger.info(f"Batches calculated: {len(result.batches)} batches")
        sys.stdout.flush()
        return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"calculate_chapter_batches error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def claim_next_batch(job_id: str) -> str:
    """
    Claim the next batch in a job.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        logger.info(f"Claiming next batch: job_id={job_id}")
        result = job_manager.claim_next_batch(job_id)
        logger.info(f"Batch claimed successfully")
        sys.stdout.flush()
        return json.dumps(result.model_dump(), ensure_ascii=False)
    except Exception as e:
        logger.error(f"claim_next_batch error: {e}", exc_info=True)
        sys.stdout.flush()
        return json.dumps({
            "error": str(e),
            "hint": "🔄 Retry this call if it failed due to timeout"
        }, ensure_ascii=False)


@mcp.tool()
@with_tool_timeout(10)
def update_knowledge_file(slug: str, filename: str, content: str, subdir: str = "") -> str:
    """
    Update or create a knowledge file.

    Timeout: 10 seconds
    If timeout occurs, retry the same call.
    """
    import logging
    logger = logging.getLogger("novelas")

    try:
        path = f"{subdir}/{filename}" if subdir else filename
        logger.info(f"Updating knowledge file: {slug}, path={path}")
        filepath = knowledge_manager.update_knowledge_file(path, content, slug=slug)
        logger.info(f"Knowledge file updated: {filepath}")
        sys.stdout.flush()
        return f"Saved: {filepath}"
    except Exception as e:
        logger.error(f"update_knowledge_file error: {e}", exc_info=True)
        sys.stdout.flush()
        return f"Error: {type(e).__name__}: {e}\n\n🔄 You can retry this call."


if __name__ == "__main__":
    import sys
    import os

    # Disable console logging in MCP mode to avoid interfering with stdio
    os.environ["NOVELAS_DISABLE_CONSOLE_LOG"] = "1"

    # Reconfigure logging for MCP mode (file only)
    import logging
    from backend.utils.logging_config import setup_logging

    # Clear existing handlers and setup file-only logging
    logger = logging.getLogger("novelas")
    logger.handlers.clear()
    logger = setup_logging(enable_console=False)

    logger.info("=" * 60)
    logger.info(f"Starting NovelAS MCP Server (PID: {os.getpid()})")
    logger.info("=" * 60)

    # Set unbuffered mode for stdio
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    # Warmup services synchronously with timeout
    logger.info("Pre-loading vector memory service...")
    try:
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Warmup timeout")

        # Windows doesn't support SIGALRM, use threading instead
        warmup_result = [False]
        warmup_error = [None]

        def warmup_with_catch():
            try:
                _warmup_services()
                warmup_result[0] = True
            except Exception as e:
                warmup_error[0] = e

        warmup_thread = threading.Thread(target=warmup_with_catch, daemon=False)
        warmup_thread.start()
        warmup_thread.join(timeout=30)  # 30秒超时

        if warmup_thread.is_alive():
            logger.warning("Warmup timed out after 30s, continuing anyway...")
        elif warmup_error[0]:
            logger.warning(f"Warmup failed: {warmup_error[0]}")
        elif warmup_result[0]:
            logger.info("Warmup completed successfully")
    except Exception as e:
        logger.warning(f"Warmup error: {e}")

    try:
        logger.info("MCP Server entering main loop...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MCP Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("MCP Server shutdown complete")
