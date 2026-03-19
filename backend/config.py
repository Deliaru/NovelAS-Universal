"""
Application configuration using Pydantic BaseSettings.
All paths are dynamically resolved - no hardcoding.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    # Application
    app_name: str = "NovelAS-Universal"
    app_version: str = "1.0.0"
    debug: bool = False

    # Paths (relative to app root by default)
    app_root: Path = Path(__file__).parent.parent.absolute()
    projects_dir: Path | None = None
    knowledge_dir: Path | None = None
    skill_definitions_dir: Path | None = None

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Vector DB
    embedding_model: str = "all-MiniLM-L6-v2"

    # Logging
    log_level: str = "INFO"
    log_file: str = "novelas.log"

    model_config = {
        "env_prefix": "NOVELAS_",
        "env_file": ".env",
    }

    def get_projects_dir(self) -> Path:
        return self.projects_dir or (self.app_root / "projects")

    def get_knowledge_dir(self) -> Path:
        return self.knowledge_dir or (self.app_root / "knowledge")

    def get_skill_definitions_dir(self) -> Path:
        return self.skill_definitions_dir or (self.app_root / "shared" / "skill_definitions")

    def get_project_path(self, slug: str) -> Path:
        return self.get_projects_dir() / slug


settings = Settings()
