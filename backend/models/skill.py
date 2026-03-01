"""
Pydantic models for skill definitions and execution.
"""

from pydantic import BaseModel, Field


class SkillInput(BaseModel):
    """A single input parameter for a skill."""

    name: str
    description: str = ""
    type: str = "string"
    required: bool = False
    default: str | None = None


class SkillDefinition(BaseModel):
    """Parsed skill definition from a SKILL.md template."""

    name: str
    description: str = ""
    inputs: list[SkillInput] = Field(default_factory=list)
    template: str = ""  # Full prompt template with {{variables}}


class SkillExecutionRequest(BaseModel):
    """Request to execute a skill."""

    params: dict[str, str] = Field(default_factory=dict)
    provider: str | None = None
    model: str | None = None


class SkillExecutionStatus(BaseModel):
    """Status of a skill execution."""

    execution_id: str
    skill_name: str
    status: str  # "running", "completed", "failed"
    progress: str = ""
    result: str | None = None
    error: str | None = None
