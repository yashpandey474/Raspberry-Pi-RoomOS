from fastapi import FastAPI
from contextlib import asynccontextmanager
from pi_controller.core.command_router import CommandRouter
from pi_controller.core.conversation_service import ConversationService
from pi_controller.core.conversation_store import ConversationStore
from pi_controller.media.adaptors.fake import FakeMediaPlayer
from pi_controller.media.contracts import Track
from pi_controller.media.service import MediaService
from pi_controller.voice.assistant import VoiceAssistant
from pi_controller.voice.audio_capture import SoundDeviceAudioCapture
from pi_controller.voice.audio_output import SoundDeviceAudioOutput
from pi_controller.voice.stt import VoskSTT
from pi_controller.voice.tts import PiperTTS
from shared.contracts import HealthResponse
from pi_controller.api.routes.media import router as media_router
from pi_controller.api.routes.assistant import router as assistant_router
from pi_controller.api.routes.voice import router as voice_router
from pi_controller.tools.registry import ToolRegistry
from pi_controller.tools.builtin import register_builtin_tools
from pi_controller.api.routes.weather import router as weather_router

import os
from pi_controller.clients.ai_engine import AIEngineClient
import logging

from shared.logging_config import configure_logging
import yaml
from pathlib import Path

from pi_controller.services.weather_service import (
    OpenMeteoWeatherService,
)
from pi_controller.tools.builtin.weather import WeatherTool



configure_logging()

logger = logging.getLogger(__name__)

def initialise_weather_service() -> OpenMeteoWeatherService:
    weather_service = OpenMeteoWeatherService(
        latitude=location["latitude"],
        longitude=location["longitude"],
        timezone_name=location["timezone"],
        database_path=storage["database_path"],
        cache_ttl_seconds=cache["ttl_seconds"],
        stale_if_error_seconds=cache["stale_if_error_seconds"],
        max_requests_per_day=limits["max_requests_per_day"],
    )
    weather_config = yaml.safe_load(
        Path("config/weather.yaml").read_text()
    )

    location = weather_config["location"]
    cache = weather_config["cache"]
    limits = weather_config["limits"]
    storage = weather_config["storage"]

    if location["latitude"] is None or location["longitude"] is None:
        raise RuntimeError("Configure the RoomOS weather coordinates.")

    return weather_service

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
    app.state.command_router = CommandRouter(
        media_service=app.state.media_service
    )

    tool_registry = ToolRegistry()
    timer_tool = register_builtin_tools(tool_registry)

    app.state.tool_registry = tool_registry
    app.state.timer_tool = timer_tool


    app.state.weather_service = initialise_weather_service()
    tool_registry.register(WeatherTool(app.state.weather_service))

    app.state.conversation_service = ConversationService(
        conversation_store=app.state.conversation_store,
        ai_engine_client=app.state.ai_engine_client,
        command_router=app.state.command_router,
        tool_registry=app.state.tool_registry
    )
    app.state.voice_assistant = VoiceAssistant(
        conversation_service=app.state.conversation_service,
        audio_capture=SoundDeviceAudioCapture(
            input_device_name="MacBook Air Microphone"
        ),
        stt=VoskSTT(
            model_path="models/stt/vosk-model-small-en-us-0.15"
        ),
        audio_output=SoundDeviceAudioOutput(),
        tts=PiperTTS(
            model_path="models/tts/en_US-lessac-medium"
        )
    )
    try:
        yield
    finally:
        # close any remaining timer processes
        await app.state.timer_tool.close()

        # close the HTTP client during shutdown to avoid resource leaks
        await app.state.ai_engine_client.close()

        await app.state.weather_service.close()

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
app.include_router(voice_router)
app.include_router(weather_router)