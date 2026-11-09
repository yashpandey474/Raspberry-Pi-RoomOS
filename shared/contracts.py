from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import StrEnum

class ChatMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: ChatMessageRole
    content: str

class ChatRequest(BaseModel):
    """What the RPi sends to the AI engine"""
    session_id: str
    messages: list[ChatMessage] = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatResponse(BaseModel):
    """What the AI engine responds back with"""
    session_id: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Whether a service is operational"""
    status: str
    service: str
    version: str

class SetVolumeRequest(BaseModel):
    volume: int = Field(ge=0, le=100)

class ChatMessageSchema(BaseModel):
    session_id: str
    role: ChatMessageRole
    content: str
    timestamp: str