"""
Abstract AI provider interface and registry.
Supports multiple LLM backends: OpenAI, Anthropic, Gemini, local models.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from backend.models.ai import AIProviderConfig, ChatResponse, Message
from backend.utils.logging_config import logger


class AIProvider(ABC):
    """Abstract interface for AI providers."""

    def __init__(self, config: AIProviderConfig):
        self.config = config

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """Send messages and get a completion."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token."""
        ...


class AIProviderRegistry:
    """Registry for managing multiple AI providers."""

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}
        self._configs: dict[str, AIProviderConfig] = {}

    def register(self, name: str, provider: AIProvider) -> None:
        self._providers[name] = provider
        logger.info(f"Registered AI provider: {name}")

    def get(self, name: str) -> AIProvider | None:
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def configure(self, config: AIProviderConfig) -> None:
        """Configure and register a provider from config."""
        self._configs[config.provider] = config

        if config.provider == "openai":
            from backend.services.openai_provider import OpenAIProvider
            self.register("openai", OpenAIProvider(config))
        elif config.provider == "anthropic":
            from backend.services.anthropic_provider import AnthropicProvider
            self.register("anthropic", AnthropicProvider(config))
        elif config.provider == "gemini":
            from backend.services.gemini_provider import GeminiProvider
            self.register("gemini", GeminiProvider(config))
        elif config.provider == "local":
            from backend.services.local_provider import LocalProvider
            self.register("local", LocalProvider(config))
        else:
            logger.warning(f"Unknown provider type: {config.provider}")


# Global registry
registry = AIProviderRegistry()
