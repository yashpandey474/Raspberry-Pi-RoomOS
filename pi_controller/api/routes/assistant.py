from typing import Annotated

from fastapi import APIRouter, Depends, Request

from shared.contracts import ChatRequest, ChatResponse
from pi_controller.clients.ai_engine import AIEngineClient

router = APIRouter(prefix="/assistant", tags=["Assistant"])


def get_ai_client(request: Request) -> AIEngineClient:
    return request.app.state.ai_engine_client


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    client: Annotated[AIEngineClient, Depends(get_ai_client)]
):
    return await client.chat(request)