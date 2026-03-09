"""
ChromaDB vector memory service for plot memory storage and retrieval.
Ported from NovelAS with enhancements:
- Per-project collections
- Exposed top_k and min_similarity parameters
- List and delete operations
- Timeout protection for blocking operations
"""

import hashlib
import json
import threading
from functools import wraps
from typing import Any, Optional

from backend.core.project_manager import get_project_path
from backend.utils.logging_config import logger

# Lazy-loaded globals
_chroma_client = None
_embedding_model = None
_init_lock = threading.Lock()


def with_timeout(seconds: int):
    """Decorator to add timeout to functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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
                logger.error(f"{func.__name__} timed out after {seconds}s")
                raise TimeoutError(f"{func.__name__} timed out after {seconds} seconds")

            if exception[0]:
                raise exception[0]

            return result[0]
        return wrapper
    return decorator


def _init_chroma_client():
    """Initialize ChromaDB client."""
    try:
        import chromadb
        from chromadb.config import Settings
        from backend.config import settings

        db_path = str(settings.app_root / "data" / "chroma_db")
        logger.info(f"Initializing ChromaDB at {db_path}")

        return chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=db_path,
            anonymized_telemetry=False,
        ))
    except Exception:
        try:
            import chromadb
            from backend.config import settings
            db_path = str(settings.app_root / "data" / "chroma_db")
            return chromadb.PersistentClient(path=db_path)
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            return None


def _init_embedding_model():
    """Initialize embedding model with local cache and retry logic."""
    try:
        from sentence_transformers import SentenceTransformer
        from backend.config import settings
        import os

        logger.info(f"Loading embedding model: {settings.embedding_model}...")

        # 强制使用本地缓存，禁用在线检查
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'

        logger.info("Creating SentenceTransformer instance (offline mode)...")
        model = SentenceTransformer(
            settings.embedding_model,
            device='cpu',
            trust_remote_code=False  # 安全起见
        )

        logger.info(f"Successfully loaded embedding model: {settings.embedding_model}")
        return model
    except Exception as e:
        logger.error(f"Sentence-transformers initialization failed: {e}", exc_info=True)
        return None


def _get_chroma():
    """Lazy-initialize ChromaDB client and embedding model."""
    global _chroma_client, _embedding_model

    # 快速检查：如果已初始化，直接返回（无锁）
    if _chroma_client is not None and _embedding_model is not None:
        return _chroma_client, _embedding_model

    # 需要初始化，获取锁
    with _init_lock:
        # 双重检查：可能其他线程已经初始化了
        if _chroma_client is not None and _embedding_model is not None:
            return _chroma_client, _embedding_model

        logger.info("Initializing vector memory service...")

        # 初始化 ChromaDB 客户端（快速操作，可以在锁内）
        if _chroma_client is None:
            _chroma_client = _init_chroma_client()
            if _chroma_client is None:
                return None, None

        # 标记正在初始化模型，然后释放锁
        need_init_model = _embedding_model is None

    # 在锁外加载模型（耗时操作）
    if need_init_model:
        logger.info("Loading embedding model outside lock...")
        max_retries = 3
        temp_model = None
        for attempt in range(max_retries):
            logger.info(f"Attempting to load embedding model (attempt {attempt + 1}/{max_retries})...")
            temp_model = _init_embedding_model()
            if temp_model is not None:
                break
            if attempt < max_retries - 1:
                logger.warning(f"Model loading failed, retrying in 2 seconds...")
                import time
                time.sleep(2)

        # 重新获取锁，设置全局变量
        with _init_lock:
            if _embedding_model is None:  # 再次检查，避免重复设置
                _embedding_model = temp_model

            if _embedding_model is None:
                logger.error("Failed to initialize embedding model after all retries")
                return _chroma_client, None

    logger.info("Vector memory service initialized successfully")
    return _chroma_client, _embedding_model


def _collection_name(slug: str) -> str:
    """Get the ChromaDB collection name for a project."""
    return f"{slug}_plot_memory"


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Ensure metadata values are ChromaDB-compatible (str, int, float, bool)."""
    sanitized = {}
    for k, v in metadata.items():
        if isinstance(v, (str, int, float, bool)):
            sanitized[k] = v
        elif v is None:
            continue
        else:
            sanitized[k] = json.dumps(v, ensure_ascii=False)
    return sanitized


def store_memory(
    slug: str,
    content: str,
    metadata: dict[str, Any],
) -> str:
    """
    Store a plot memory entry.

    Args:
        slug: Project slug.
        content: Text content to store.
        metadata: Must include at least {volume, chapter, type}.

    Returns:
        The generated memory ID.
    """
    client, model = _get_chroma()
    if client is None or model is None:
        raise RuntimeError("Vector DB not available")

    collection = client.get_or_create_collection(_collection_name(slug))

    vol = metadata.get("volume", 0)
    ch = metadata.get("chapter", 0)
    mem_type = metadata.get("type", "event")
    content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
    memory_id = f"vol{vol}_ch{ch}_{mem_type}_{content_hash}"

    embedding = model.encode([content])[0].tolist()
    sanitized = _sanitize_metadata(metadata)

    collection.upsert(
        ids=[memory_id],
        documents=[content],
        metadatas=[sanitized],
        embeddings=[embedding],
    )

    logger.info(f"Stored memory {memory_id} in {_collection_name(slug)}")
    return memory_id


def store_memory_batch(
    slug: str,
    items: list[dict],
) -> int:
    """
    Batch store multiple memory entries.

    Args:
        items: List of {content: str, metadata: dict} objects.

    Returns:
        Number of items stored.
    """
    client, model = _get_chroma()
    if client is None or model is None:
        raise RuntimeError("Vector DB not available")

    collection = client.get_or_create_collection(_collection_name(slug))

    ids = []
    documents = []
    metadatas = []
    contents_for_embed = []

    for item in items:
        content = item["content"]
        metadata = item.get("metadata", {})
        vol = metadata.get("volume", 0)
        ch = metadata.get("chapter", 0)
        mem_type = metadata.get("type", "event")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
        memory_id = f"vol{vol}_ch{ch}_{mem_type}_{content_hash}"

        ids.append(memory_id)
        documents.append(content)
        metadatas.append(_sanitize_metadata(metadata))
        contents_for_embed.append(content)

    embeddings = model.encode(contents_for_embed).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    logger.info(f"Batch stored {len(items)} memories in {_collection_name(slug)}")
    return len(items)


@with_timeout(30)
def query_memory(
    slug: str,
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.0,
) -> list[dict]:
    """
    Semantic search in plot memory with timeout protection.

    Args:
        slug: Project slug.
        query: Search query text.
        top_k: Maximum results to return.
        min_similarity: Minimum similarity threshold (0.0-1.0).

    Returns:
        List of {id, content, metadata, distance} dicts.
    """
    client, model = _get_chroma()
    if client is None or model is None:
        logger.warning("Vector DB not available, returning empty results")
        return []

    try:
        collection = client.get_or_create_collection(_collection_name(slug))
    except Exception as e:
        logger.error(f"Failed to get collection: {e}")
        return []

    logger.debug(f"Encoding query: {query[:50]}...")
    query_embedding = model.encode([query])[0].tolist()
    logger.debug("Query encoding completed")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    memories = []
    if results and results["ids"] and results["ids"][0]:
        for i, memory_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results.get("distances") else 0
            # ChromaDB returns L2 distance; convert to similarity
            similarity = 1.0 / (1.0 + distance)

            if similarity < min_similarity:
                continue

            memories.append({
                "id": memory_id,
                "content": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": distance,
                "similarity": round(similarity, 4),
            })

    return memories


def list_memories(slug: str, limit: int = 100) -> list[dict]:
    """List all stored memories for a project."""
    client, _ = _get_chroma()
    if client is None:
        return []

    try:
        collection = client.get_or_create_collection(_collection_name(slug))
        results = collection.get(limit=limit)
        memories = []
        if results and results["ids"]:
            for i, memory_id in enumerate(results["ids"]):
                memories.append({
                    "id": memory_id,
                    "content": results["documents"][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                })
        return memories
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        return []


def delete_memory(slug: str, memory_id: str) -> bool:
    """Delete a specific memory entry."""
    client, _ = _get_chroma()
    if client is None:
        return False

    try:
        collection = client.get_or_create_collection(_collection_name(slug))
        collection.delete(ids=[memory_id])
        logger.info(f"Deleted memory {memory_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        return False


def get_memory_count(slug: str) -> int:
    """Get the number of stored memories for a project."""
    client, _ = _get_chroma()
    if client is None:
        return 0

    try:
        collection = client.get_or_create_collection(_collection_name(slug))
        return collection.count()
    except Exception:
        return 0
