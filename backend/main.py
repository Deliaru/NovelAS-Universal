"""
NovelAS-Universal FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.utils.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Projects dir: {settings.get_projects_dir()}")
    logger.info(f"Knowledge dir: {settings.get_knowledge_dir()}")

    # Ensure base directories exist
    settings.get_projects_dir().mkdir(parents=True, exist_ok=True)
    settings.get_knowledge_dir().mkdir(parents=True, exist_ok=True)

    yield

    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}


# Import and include routers
from backend.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api")
