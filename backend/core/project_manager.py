"""
Project lifecycle management.
Creates, lists, loads, and deletes novel projects.
Each project is an isolated directory with its own data, lore, and Git repo.
"""

import shutil
from pathlib import Path

import yaml

from backend.config import settings
from backend.models.project import (
    CreateProjectRequest,
    ProjectConfig,
    ProjectSummary,
    VolumeConfig,
)
from backend.utils.logging_config import logger

# Standard subdirectories created for every project
_PROJECT_DIRS = [
    "source",
    "chapters",
    "chapters/extras",
    "drafts",
    "lore_database/characters",
    "lore_database/factions",
    "lore_database/worldview",
    "lore_database/items",
    "vector_db",
    "knowledge",
    "seed",
]


def _project_root(slug: str) -> Path:
    return settings.get_projects_dir() / slug


def _read_config(project_path: Path) -> ProjectConfig:
    """Read project.yaml from a project directory."""
    config_file = project_path / "project.yaml"
    if not config_file.exists():
        raise FileNotFoundError(f"project.yaml not found in {project_path}")
    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ProjectConfig(**data)


def _write_config(project_path: Path, config: ProjectConfig) -> None:
    """Write project.yaml to a project directory."""
    config_file = project_path / "project.yaml"
    data = config.model_dump(mode="json")
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def list_projects() -> list[ProjectSummary]:
    """List all projects in the projects directory."""
    projects_dir = settings.get_projects_dir()
    if not projects_dir.exists():
        return []

    results = []
    for entry in sorted(projects_dir.iterdir()):
        if not entry.is_dir():
            continue
        config_file = entry / "project.yaml"
        if not config_file.exists():
            continue
        try:
            config = _read_config(entry)
            # Count chapters and lore entries
            chapter_count = sum(
                1
                for f in (entry / "chapters").rglob("*.md")
                if f.is_file()
            ) if (entry / "chapters").exists() else 0

            lore_count = sum(
                1
                for f in (entry / "lore_database").rglob("*.md")
                if f.is_file()
            ) if (entry / "lore_database").exists() else 0

            results.append(
                ProjectSummary(
                    slug=config.slug,
                    name=config.name,
                    description=config.description,
                    volume_count=len(config.volumes),
                    chapter_count=chapter_count,
                    lore_count=lore_count,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to read project {entry.name}: {e}")
            continue

    return results


def create_project(request: CreateProjectRequest) -> ProjectConfig:
    """
    Create a new project with standard directory structure.

    Raises:
        FileExistsError: If a project with the same slug already exists.
    """
    project_path = _project_root(request.slug)
    if project_path.exists():
        raise FileExistsError(f"Project '{request.slug}' already exists")

    # Create directory structure
    project_path.mkdir(parents=True)
    for subdir in _PROJECT_DIRS:
        (project_path / subdir).mkdir(parents=True, exist_ok=True)

    # Create volume directories
    for vol in request.volumes:
        (project_path / "chapters" / f"vol{vol.number}").mkdir(exist_ok=True)
        (project_path / "drafts" / f"vol{vol.number}").mkdir(parents=True, exist_ok=True)
        if vol.source_dir:
            (project_path / vol.source_dir).mkdir(parents=True, exist_ok=True)

    # Write config
    config = ProjectConfig(
        name=request.name,
        slug=request.slug,
        description=request.description,
        volumes=request.volumes,
        settings=request.settings,
    )
    _write_config(project_path, config)

    # Initialize Git repo for lore versioning
    try:
        from backend.utils.git_ops import init_repo
        init_repo(project_path)
    except Exception as e:
        logger.warning(f"Failed to init git repo for project {request.slug}: {e}")

    logger.info(f"Created project: {request.slug}")
    return config


def get_project(slug: str) -> ProjectConfig:
    """
    Load a project configuration.

    Raises:
        FileNotFoundError: If project doesn't exist.
    """
    project_path = _project_root(slug)
    if not project_path.exists():
        raise FileNotFoundError(f"Project '{slug}' not found")
    return _read_config(project_path)


def update_project(slug: str, config: ProjectConfig) -> ProjectConfig:
    """Update a project's configuration."""
    project_path = _project_root(slug)
    if not project_path.exists():
        raise FileNotFoundError(f"Project '{slug}' not found")
    _write_config(project_path, config)
    return config


def delete_project(slug: str) -> None:
    """
    Delete a project and all its data.

    Raises:
        FileNotFoundError: If project doesn't exist.
    """
    project_path = _project_root(slug)
    if not project_path.exists():
        raise FileNotFoundError(f"Project '{slug}' not found")
    shutil.rmtree(project_path)
    logger.info(f"Deleted project: {slug}")


def get_project_path(slug: str) -> Path:
    """Get the filesystem path for a project. Raises if not found."""
    project_path = _project_root(slug)
    if not project_path.exists():
        raise FileNotFoundError(f"Project '{slug}' not found")
    return project_path
