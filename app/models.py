from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    url: str
