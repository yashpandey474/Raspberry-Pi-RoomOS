from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pi_controller.media.adaptors.fake import FakeMediaPlayer
from pi_controller.media.contracts import Track
from pi_controller.media.service import MediaService
from shared.contracts import HealthResponse
from pi_controller.api.routes.media import router as media_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    player = FakeMediaPlayer(tracks=[
        Track(id="1", title="Track One", artist="Artist One"),
        Track(id="2", title="Track Two", artist="Artist Two"),
        Track(id="3", title="Track Three", artist="Artist Three"),
    ])

    app.state.media_service = MediaService(player)

    yield

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