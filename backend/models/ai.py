"""
Pydantic models for AI provider integration.
"""

from pydantic import BaseModel, Field


class AIProviderConfig(BaseModel):
    """Configuration for an AI provider."""

    provider: str  # "openai", "anthropic", "gemini", "local"
    api_key: str | None = None
    model: str = ""
    base_url: str | None = None  # For local/custom endpoints
    temperature: float = 0.7
    max_tokens: int = 4096


class Message(BaseModel):
    """A chat message."""

    role: str  # "system", "user", "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for AI chat completion."""

    messages: list[Message]
    provider: str | None = None  # Override default provider
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class ChatResponse(BaseModel):
    """Response from AI chat completion."""

    content: str
    model: str
    provider: str
    usage: dict = Field(default_factory=dict)
