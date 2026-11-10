from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class OllamaConfig(BaseModel):
    model: str = Field(min_length=1)
    base_url: str
    request_timeout_seconds: float = Field(gt=0)
    connect_timeout_seconds: float = Field(gt=0)


class AIEngineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["ollama"]
    ollama: OllamaConfig


def load_config() -> AIEngineConfig:
    config_path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "ai_engine.yaml"
    )

    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)

    return AIEngineConfig.model_validate(raw_config)