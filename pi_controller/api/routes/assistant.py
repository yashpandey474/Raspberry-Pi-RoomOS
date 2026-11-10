from typing import Annotated

from fastapi import APIRouter, Depends, Request

from pi_controller.core.conversation_service import ConversationService
from shared.contracts import AIEngineChatRequest, AssistantChatRequest, ChatResponse
from pi_controller.clients.ai_engine import AIEngineClient

router = APIRouter(prefix="/assistant", tags=["Assistant"])


def get_ai_client(request: Request) -> AIEngineClient:
    return request.app.state.ai_engine_client

def get_conversation_service(request: Request) -> ConversationService:
    return request.app.state.conversation_service

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: AssistantChatRequest,
    service: Annotated[ConversationService, Depends(get_conversation_service)]
):

    return await service.chat(request)