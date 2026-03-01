"""
DOCX conversion REST API endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.project_manager import get_project_path
from backend.utils.docx_converter import DocxConverter

router = APIRouter(prefix="/projects/{slug}/convert", tags=["converter"])


class ConvertRequest(BaseModel):
    volume_dir: str | None = None  # Specific volume dir name, or None for all


@router.post("")
async def convert_docx(slug: str, request: ConvertRequest):
    """
    Trigger DOCX to Markdown conversion for a project.
    Converts files from source/ to chapters/.
    """
    try:
        project_path = get_project_path(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    converter = DocxConverter(project_path)
    source_dir = project_path / "source"

    if not source_dir.exists():
        raise HTTPException(status_code=404, detail="No source directory found")

    if request.volume_dir:
        vol_path = source_dir / request.volume_dir
        if not vol_path.exists():
            raise HTTPException(status_code=404, detail=f"Volume dir not found: {request.volume_dir}")
        results = converter.convert_volume(vol_path)
    else:
        results = converter.convert_all()

    return {
        "status": "ok",
        "converted": len(results),
        "files": [str(p.name) for p in results],
    }
