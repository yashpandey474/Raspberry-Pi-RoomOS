from pydantic import BaseModel, Field
from enum import StrEnum

class SetVolumeRequest(BaseModel):
    volume: int = Field(ge=0, le=100)

class LLMMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"