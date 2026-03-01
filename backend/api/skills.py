"""
Skill execution REST API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.skill import SkillDefinition, SkillExecutionRequest
from backend.services import skill_executor

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillDefinition])
async def list_skills():
    """List all available skills."""
    return skill_executor.list_skills()


@router.get("/{name}", response_model=SkillDefinition)
async def get_skill(name: str):
    """Get a specific skill definition."""
    skill = skill_executor.get_skill(name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    return skill


@router.post("/{name}/execute")
async def execute_skill(name: str, request: SkillExecutionRequest):
    """
    Execute a skill with streaming output.
    Returns a Server-Sent Events stream.
    """

    async def event_stream():
        async for chunk in skill_executor.execute_skill(
            name, request.params, request.provider
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
