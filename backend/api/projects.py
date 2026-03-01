"""
Project management REST API endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core import project_manager
from backend.models.project import CreateProjectRequest, ProjectConfig, ProjectSummary

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummary])
async def list_projects():
    """List all available projects."""
    return project_manager.list_projects()


@router.post("", response_model=ProjectConfig, status_code=201)
async def create_project(request: CreateProjectRequest):
    """Create a new novel project."""
    try:
        return project_manager.create_project(request)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{slug}", response_model=ProjectConfig)
async def get_project(slug: str):
    """Get project configuration."""
    try:
        return project_manager.get_project(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{slug}", response_model=ProjectConfig)
async def update_project(slug: str, config: ProjectConfig):
    """Update project configuration."""
    try:
        return project_manager.update_project(slug, config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{slug}", status_code=204)
async def delete_project(slug: str):
    """Delete a project and all its data."""
    try:
        project_manager.delete_project(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


class ImportRequest(BaseModel):
    source_dir: str  # Path to original NovelAS project
    name: str
    description: str = ""


@router.post("/{slug}/import")
async def import_from_novelas(slug: str, request: ImportRequest):
    """Import data from an existing NovelAS project."""
    from backend.utils.importer import import_from_novelas

    try:
        stats = import_from_novelas(
            source_dir=request.source_dir,
            project_name=request.name,
            project_slug=slug,
            description=request.description,
        )
        return {"status": "ok", "stats": stats}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
