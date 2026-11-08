from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """What the RPi sends to the AI engine"""
    session_id: str
    message: str = Field(min_length=1)
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