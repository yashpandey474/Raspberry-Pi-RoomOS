from fastapi import FastAPI
from shared.contracts import HealthResponse

app = FastAPI(
    title="RoomOS AI Engine",
    version="0.1.0"
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="ai-engine",
        version="0.1.0"
    )