from fastapi.params import Depends
from typing_extensions import Annotated

from fastapi import APIRouter, FastAPI, Request

from pi_controller.core.models import SetVolumeRequest
from pi_controller.media.contracts import PlaybackState
from pi_controller.media.service import MediaService


router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "roomos-core-media",
        "version": "0.1.0"
    }

def get_media_service(request: Request) -> MediaService:
    return request.app.state.media_service

@router.get("/state", response_model=PlaybackState)
def get_state(
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.get_state()

@router.post("/play", response_model=PlaybackState)
def play(
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.play()

@router.post("/pause", response_model=PlaybackState)
def pause(
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.pause()

@router.post("/next", response_model=PlaybackState)
def next(
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.next()

@router.post("/previous", response_model=PlaybackState)
def previous(
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.previous()

@router.post("/volume", response_model=PlaybackState)
def set_volume(
    volume_request: SetVolumeRequest,
    service: Annotated[MediaService, Depends(get_media_service)]
):
    return service.set_volume(volume_request.volume)