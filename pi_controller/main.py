from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pi_controller.core.conversation_service import ConversationService
from pi_controller.core.conversation_store import ConversationStore
from pi_controller.media.adaptors.fake import FakeMediaPlayer
from pi_controller.media.contracts import Track
from pi_controller.media.service import MediaService
from shared.contracts import HealthResponse
from pi_controller.api.routes.media import router as media_router
from pi_controller.api.routes.assistant import router as assistant_router

import os
from pi_controller.clients.ai_engine import AIEngineClient



@asynccontextmanager
async def lifespan(app: FastAPI):
    player = FakeMediaPlayer(tracks=[
        Track(id="1", title="Track One", artist="Artist One"),
        Track(id="2", title="Track Two", artist="Artist Two"),
        Track(id="3", title="Track Three", artist="Artist Three"),
    ])

    app.state.media_service = MediaService(player)
    app.state.ai_engine_client = AIEngineClient(
        base_url=os.getenv(
            "ROOMOS_AI_ENGINE_URL",
            "http://127.0.0.1:8001"
        )
    )
    app.state.conversation_store = ConversationStore()
    app.state.conversation_service = ConversationService(
        conversation_store=app.state.conversation_store,
        ai_engine_client=app.state.ai_engine_client
    )
    try:
        yield
    finally:
        # close the HTTP client during shutdown to avoid resource leaks
        await app.state.ai_engine_client.close()

app = FastAPI(
    title="RoomOS Core",
    version="0.1.0",
    description="Local-first room operating system",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    # TODO: Return RoomOS Core health information
    return HealthResponse(
        status="ok",
        service="roomos-core",
        version="0.1.0"
    )

app.include_router(media_router)
app.include_router(assistant_router)