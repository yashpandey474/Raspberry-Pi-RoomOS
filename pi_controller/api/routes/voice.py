from fastapi.params import Depends
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from fastapi import APIRouter, FastAPI, Request

from pi_controller.media.contracts import PlaybackState
from pi_controller.media.service import MediaService
from pi_controller.voice.assistant import VoiceAssistant
from shared.contracts import SetVolumeRequest


router = APIRouter(prefix="/voice", tags=["Voice"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "roomos-core-voice",
        "version": "0.1.0"
    }

class VoiceInteractionRequest(BaseModel):
    session_id: str = Field(min_length=1)


def get_voice_assistant(request: Request) -> VoiceAssistant:
    return request.app.state.voice_assistant

@router.post("/interact")
async def play(
    body: VoiceInteractionRequest,
    assistant: Annotated[VoiceAssistant, Depends(get_voice_assistant)],
):
    await assistant.run_once(session_id=body.session_id)
    return {
        "status": "completed",
        "session_id": body.session_id,
    }
    
