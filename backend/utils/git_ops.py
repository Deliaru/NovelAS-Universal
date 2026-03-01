"""
Git version control operations for lore versioning.
Each project has its own Git repository for tracking lore changes.
"""

from pathlib import Path
from typing import Optional

from backend.utils.logging_config import logger

try:
    from git import Repo, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    logger.warning("GitPython not installed. Git versioning disabled.")


def init_repo(project_path: Path) -> bool:
    """Initialize a Git repository in the project directory."""
    if not GIT_AVAILABLE:
        return False

    git_dir = project_path / ".git"
    if git_dir.exists():
        logger.info(f"Git repo already exists at {project_path}")
        return True

    try:
        repo = Repo.init(project_path)
        # Create initial .gitignore
        gitignore = project_path / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(
                "vector_db/\nsource/\n*.log\n__pycache__/\n",
                encoding="utf-8",
            )
        repo.index.add([".gitignore"])
        repo.index.commit("Initial commit")
        logger.info(f"Initialized git repo at {project_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to init git repo: {e}")
        return False


def commit_changes(
    project_path: Path,
    files: list[str],
    message: str,
) -> Optional[str]:
    """
    Stage and commit specific files.

    Args:
        project_path: Project root directory.
        files: List of relative file paths to stage.
        message: Commit message.

    Returns:
        Commit SHA hex string, or None if failed.
    """
    if not GIT_AVAILABLE:
        return None

    try:
        repo = Repo(project_path)
        repo.index.add(files)
        commit = repo.index.commit(message)
        logger.info(f"Git commit {commit.hexsha[:8]}: {message}")
        return commit.hexsha
    except InvalidGitRepositoryError:
        logger.warning(f"Not a git repo: {project_path}")
        return None
    except Exception as e:
        logger.error(f"Git commit failed: {e}")
        return None


def get_file_history(
    project_path: Path,
    file_path: str,
    max_entries: int = 20,
) -> list[dict]:
    """
    Get commit history for a specific file.

    Returns list of {sha, message, date, author} dicts.
    """
    if not GIT_AVAILABLE:
        return []

    try:
        repo = Repo(project_path)
        commits = list(repo.iter_commits(paths=file_path, max_count=max_entries))
        return [
            {
                "sha": c.hexsha[:8],
                "message": c.message.strip(),
                "date": c.committed_datetime.isoformat(),
                "author": str(c.author),
            }
            for c in commits
        ]
    except Exception as e:
        logger.error(f"Failed to get git history: {e}")
        return []
