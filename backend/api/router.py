"""
Central API router aggregator.
All route modules are included here.
"""

from fastapi import APIRouter

from backend.api.projects import router as projects_router
from backend.api.chapters import router as chapters_router
from backend.api.lore import router as lore_router
from backend.api.memory import router as memory_router
from backend.api.jobs import router as jobs_router
from backend.api.knowledge import router as knowledge_router
from backend.api.converter import router as converter_router

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(chapters_router)
api_router.include_router(lore_router)
api_router.include_router(memory_router)
api_router.include_router(jobs_router)
api_router.include_router(knowledge_router)
api_router.include_router(converter_router)

from backend.api.skills import router as skills_router
from backend.api.ai import router as ai_router

api_router.include_router(skills_router)
api_router.include_router(ai_router)
