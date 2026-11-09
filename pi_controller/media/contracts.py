from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


class PlaybackStatus(StrEnum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class Track(BaseModel):
    id: str
    title: str
    artist: str | None = None


class PlaybackState(BaseModel):
    status: PlaybackStatus
    current_track: Track | None = None
    volume: int = Field(default=50, ge=0, le=100)
    position_seconds: float = Field(default=0, ge=0)


class MediaPlayer(Protocol):
    def play(self) -> PlaybackState: ...
    def pause(self) -> PlaybackState: ...
    def next(self) -> PlaybackState: ...
    def previous(self) -> PlaybackState: ...
    def set_volume(self, volume: int) -> PlaybackState: ...
    def get_state(self) -> PlaybackState: ...