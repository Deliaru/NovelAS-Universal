"""
ChromaDB vector memory service for plot memory storage and retrieval.
Ported from NovelAS with enhancements:
- Per-project collections
- Exposed top_k and min_similarity parameters
- List and delete operations
"""

import hashlib
import json
from typing import Any, Optional

from backend.core.project_manager import get_project_path
from backend.utils.logging_config import logger

# Lazy-loaded globals
_chroma_client = None
_embedding_model = None


def _get_chroma():
    """Lazy-initialize ChromaDB client and embedding model."""
    global _chroma_client, _embedding_model

    if _chroma_client is not None:
        return _chroma_client, _embedding_model

    try:
        import chromadb
        from chromadb.config import Settings

        # Use a shared database directory
        from backend.config import settings
        db_path = str(settings.app_root / "data" / "chroma_db")

        _chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=db_path,
            anonymized_telemetry=False,
        ))
    except Exception:
        try:
            import chromadb
            from backend.config import settings
            db_path = str(settings.app_root / "data" / "chroma_db")
            _chroma_client = chromadb.PersistentClient(path=db_path)
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            return None, None

    try:
        from sentence_transformers import SentenceTransformer
        from backend.config import settings
        _embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info(f"Loaded embedding model: {settings.embedding_model}")
    except Exception as e:
        logger.error(f"Sentence-transformers initialization failed: {e}")
        return _chroma_client, None

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


def query_memory(
    slug: str,
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.0,
) -> list[dict]:
    """
    Semantic search in plot memory.

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
        return []

    try:
        collection = client.get_or_create_collection(_collection_name(slug))
    except Exception as e:
        logger.error(f"Failed to get collection: {e}")
        return []

    query_embedding = model.encode([query])[0].tolist()

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
