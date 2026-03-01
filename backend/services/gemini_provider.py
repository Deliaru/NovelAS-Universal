"""
Google Gemini AI provider.
"""

from typing import AsyncIterator

import httpx

from backend.models.ai import AIProviderConfig, ChatResponse, Message
from backend.services.ai_provider import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""

    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.default_model = config.model or "gemini-2.0-flash"

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        model = model or self.default_model

        # Convert messages to Gemini format
        system_instruction = ""
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}],
                })

        body: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature or self.config.temperature,
                "maxOutputTokens": max_tokens or self.config.max_tokens,
            },
        }
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
            f":generateContent?key={self.config.api_key}"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=body,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})

        return ChatResponse(
            content=content,
            model=model,
            provider="gemini",
            usage=usage,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        # Gemini streaming via streamGenerateContent
        model = model or self.default_model

        system_instruction = ""
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        body: dict = {"contents": contents}
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
            f":streamGenerateContent?alt=sse&key={self.config.api_key}"
        )

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=body, timeout=120.0) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        try:
                            chunk = json.loads(line[6:])
                            parts = chunk.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "text" in part:
                                    yield part["text"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
