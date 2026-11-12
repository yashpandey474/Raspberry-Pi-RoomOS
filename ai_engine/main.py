import os
import httpx
from contextlib import asynccontextmanager
from typing import Annotated
from datetime import datetime
from fastapi import FastAPI, Depends, Request, HTTPException

from shared.contracts import AIEngineChatRequest, ChatResponse, HealthResponse
from ai_engine.providers.ollama import OllamaProvider
from ai_engine.config import load_config
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    provider = OllamaProvider(
        model=config.ollama.model,
        base_url=config.ollama.base_url,
        request_timeout_seconds=config.ollama.request_timeout_seconds,
        connect_timeout_seconds=config.ollama.connect_timeout_seconds,
        context_length=config.ollama.context_length,
        max_tokens=config.ollama.max_tokens
    )
    logger.info(
        "AI Engine initialized: provider=%s, model=%s",
        config.provider,
        config.ollama.model
    )
    
    app.state.ollama = provider

    try:
        yield
    finally:
        await provider.close()


app = FastAPI(
    title="RoomOS AI Engine",
    version="0.1.0",
    lifespan=lifespan
)


def get_provider(request: Request) -> OllamaProvider:
    return request.app.state.ollama


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    request: AIEngineChatRequest,
    provider: Annotated[OllamaProvider, Depends(get_provider)]
):
    try:
        start_time = datetime.utcnow().isoformat()
        answer = await provider.chat(request.messages)
        time_taken = (datetime.utcnow() - datetime.fromisoformat(start_time)).total_seconds()
        logger.info(
            "Chat request processed: session_id=%s, time_taken=%.2f seconds",
            request.session_id,
            time_taken
        )
        
        return ChatResponse(
            session_id=request.session_id,
            response=answer
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Local LLM provider request failed"
        ) from exc