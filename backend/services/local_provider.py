"""
Local model provider (Ollama and compatible OpenAI-format servers).
"""

from typing import AsyncIterator

from backend.models.ai import AIProviderConfig, ChatResponse, Message
from backend.services.openai_provider import OpenAIProvider


class LocalProvider(OpenAIProvider):
    """
    Local model provider.
    Uses OpenAI-compatible API format (works with Ollama, LM Studio, etc.)
    """

    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434/v1"
        self.default_model = config.model or "llama3.2"

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        result = await super().complete(messages, model, temperature, max_tokens)
        result.provider = "local"
        return result

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        async for token in super().stream(messages, model):
            yield token
