"""
Vector memory REST API endpoints.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services import vector_memory

router = APIRouter(prefix="/projects/{slug}/memory", tags=["memory"])


class StoreMemoryRequest(BaseModel):
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StoreMemoryBatchRequest(BaseModel):
    items: list[dict[str, Any]]


class QueryMemoryRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.0


@router.post("/store")
async def store_memory(slug: str, request: StoreMemoryRequest):
    """Store a single plot memory entry."""
    try:
        memory_id = vector_memory.store_memory(slug, request.content, request.metadata)
        return {"status": "ok", "id": memory_id}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/store-batch")
async def store_memory_batch(slug: str, request: StoreMemoryBatchRequest):
    """Batch store multiple memory entries."""
    try:
        count = vector_memory.store_memory_batch(slug, request.items)
        return {"status": "ok", "count": count}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/query")
async def query_memory(slug: str, request: QueryMemoryRequest):
    """Semantic search in plot memory."""
    results = vector_memory.query_memory(
        slug, request.query, request.top_k, request.min_similarity
    )
    return {"results": results, "count": len(results)}


@router.get("")
async def list_memories(slug: str, limit: int = 100):
    """List all stored memories."""
    memories = vector_memory.list_memories(slug, limit)
    return {"memories": memories, "count": len(memories)}


@router.delete("/{memory_id}")
async def delete_memory(slug: str, memory_id: str):
    """Delete a specific memory entry."""
    success = vector_memory.delete_memory(slug, memory_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete memory")
    return {"status": "ok"}


@router.get("/count")
async def memory_count(slug: str):
    """Get the number of stored memories."""
    return {"count": vector_memory.get_memory_count(slug)}
