import os
import httpx
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request, HTTPException

from shared.contracts import ChatRequest, ChatResponse, HealthResponse
from ai_engine.providers.ollama import OllamaProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider = OllamaProvider(
        model=os.environ["ROOMOS_OLLAMA_MODEL"]
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
    request: ChatRequest,
    provider: Annotated[OllamaProvider, Depends(get_provider)]
):
    try:
        answer = await provider.chat(request.message)

        return ChatResponse(
            session_id=request.session_id,
            response=answer
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Local LLM provider request failed"
        ) from exc