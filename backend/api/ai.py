"""
AI provider configuration and chat REST API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.ai import AIProviderConfig, ChatRequest, ChatResponse
from backend.services.ai_provider import registry

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers")
async def list_providers():
    """List configured AI providers."""
    return {"providers": registry.list_providers()}


@router.post("/config")
async def configure_provider(config: AIProviderConfig):
    """Configure an AI provider with API key."""
    try:
        registry.configure(config)
        return {"status": "ok", "provider": config.provider}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message to the configured AI provider."""
    provider_name = request.provider or (
        registry.list_providers()[0] if registry.list_providers() else None
    )
    if not provider_name:
        raise HTTPException(status_code=400, detail="No AI provider configured")

    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=400, detail=f"Provider '{provider_name}' not configured")

    try:
        return await provider.complete(
            request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream a chat response via SSE."""
    provider_name = request.provider or (
        registry.list_providers()[0] if registry.list_providers() else None
    )
    if not provider_name:
        raise HTTPException(status_code=400, detail="No AI provider configured")

    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=400, detail=f"Provider '{provider_name}' not configured")

    async def event_stream():
        try:
            async for token in provider.stream(request.messages, model=request.model):
                yield f"data: {token}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
