from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import StrEnum

class ChatMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool" 

# Related to supporting tool calls made by LLM
class ToolCallFunction(BaseModel):
    index: int | None = None
    name: str
    arguments: dict[str, Any]

class ToolCall(BaseModel):
    id: str | None = None
    function: ToolCallFunction

class ChatMessage(BaseModel):
    role: ChatMessageRole
    content: str
    thinking: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_name: str | None = None

class ChatResponse(BaseModel):
    """What the AI engine responds back with"""
    session_id: str
    response: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    thinking: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)

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

# Chat request to the service running on the rpi
class AssistantChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)

# Chat request to the AI engine
class AIEngineChatRequest(BaseModel):
    session_id: str
    messages: list[ChatMessage]
    tools: list[dict[str, Any]] = Field(default_factory=list)



