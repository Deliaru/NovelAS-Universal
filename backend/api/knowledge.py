"""
Knowledge file management REST API endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core import knowledge_manager

router = APIRouter(tags=["knowledge"])


class UpdateKnowledgeRequest(BaseModel):
    content: str


@router.get("/knowledge")
async def list_shared_knowledge():
    """List all shared knowledge files."""
    return knowledge_manager.list_shared_knowledge()


@router.get("/projects/{slug}/knowledge")
async def list_project_knowledge(slug: str):
    """List project-specific knowledge files."""
    try:
        return knowledge_manager.list_project_knowledge(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/knowledge/{path:path}")
async def read_knowledge(path: str, slug: str | None = None):
    """Read a knowledge file."""
    try:
        content = knowledge_manager.read_knowledge_file(path, slug)
        return {"path": path, "content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/knowledge/{path:path}")
async def update_knowledge(path: str, request: UpdateKnowledgeRequest, slug: str | None = None):
    """Create or update a knowledge file."""
    filepath = knowledge_manager.update_knowledge_file(path, request.content, slug)
    return {"status": "ok", "path": filepath}
