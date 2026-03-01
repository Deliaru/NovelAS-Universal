"""
Skill execution engine.
Loads skill templates, substitutes variables, orchestrates AI + tool calls.
"""

import re
import uuid
from pathlib import Path
from typing import AsyncIterator

from backend.config import settings
from backend.models.ai import Message
from backend.models.skill import SkillDefinition, SkillExecutionStatus, SkillInput
from backend.services.ai_provider import registry
from backend.utils.logging_config import logger


def _parse_skill_file(filepath: Path) -> SkillDefinition:
    """Parse a SKILL.md file into a SkillDefinition."""
    content = filepath.read_text(encoding="utf-8")

    # Extract name from filename or first heading
    name = filepath.stem
    if filepath.name == "SKILL.md":
        name = filepath.parent.name

    # Extract description from first paragraph
    description = ""
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
            description = stripped
            break

    # Extract input parameters from {{variable}} patterns
    variables = set(re.findall(r"\{\{(\w+)\}\}", content))
    inputs = [
        SkillInput(name=var, description=f"Parameter: {var}")
        for var in sorted(variables)
    ]

    return SkillDefinition(
        name=name,
        description=description,
        inputs=inputs,
        template=content,
    )


def list_skills() -> list[SkillDefinition]:
    """List all available skill definitions."""
    skill_dir = settings.get_skill_definitions_dir()
    if not skill_dir.exists():
        return []

    skills = []
    for filepath in sorted(skill_dir.glob("*.md")):
        try:
            skills.append(_parse_skill_file(filepath))
        except Exception as e:
            logger.warning(f"Failed to parse skill {filepath.name}: {e}")

    # Also check for SKILL.md in subdirectories (Gemini CLI format)
    for subdir in sorted(skill_dir.iterdir()):
        if subdir.is_dir():
            skill_file = subdir / "SKILL.md"
            if skill_file.exists():
                try:
                    skills.append(_parse_skill_file(skill_file))
                except Exception as e:
                    logger.warning(f"Failed to parse skill {subdir.name}: {e}")

    return skills


def get_skill(name: str) -> SkillDefinition | None:
    """Get a specific skill by name."""
    skill_dir = settings.get_skill_definitions_dir()

    # Try direct file
    direct = skill_dir / f"{name}.md"
    if direct.exists():
        return _parse_skill_file(direct)

    # Try subdirectory (Gemini CLI format)
    subdir = skill_dir / name / "SKILL.md"
    if subdir.exists():
        return _parse_skill_file(subdir)

    return None


def _substitute_variables(template: str, params: dict[str, str]) -> str:
    """Replace {{variable}} placeholders with actual values."""
    result = template
    for key, value in params.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


async def execute_skill(
    skill_name: str,
    params: dict[str, str],
    provider_name: str | None = None,
) -> AsyncIterator[str]:
    """
    Execute a skill and stream results.

    Yields progress text chunks as the skill runs.
    """
    skill = get_skill(skill_name)
    if not skill:
        yield f"Error: Skill '{skill_name}' not found"
        return

    provider = registry.get(provider_name or "openai")
    if not provider:
        available = registry.list_providers()
        if not available:
            yield "Error: No AI provider configured. Please configure an API key in Settings."
            return
        provider = registry.get(available[0])

    # Build prompt from template
    prompt = _substitute_variables(skill.template, params)

    # Send to AI
    messages = [
        Message(role="system", content="You are a novel creation assistant. Follow the skill instructions precisely."),
        Message(role="user", content=prompt),
    ]

    try:
        async for token in provider.stream(messages):
            yield token
    except Exception as e:
        logger.error(f"Skill execution failed: {e}")
        yield f"\n\nError during execution: {e}"
