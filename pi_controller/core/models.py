from pydantic import BaseModel, Field


class SetVolumeRequest(BaseModel):
    volume: int = Field(ge=0, le=100)