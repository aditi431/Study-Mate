from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class NoteCreate(BaseModel):
    title: Title
    description: Description
    topics_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")


class NoteUpdate(BaseModel):
    title: Title | None = None
    description: Description | None = None
    topics_count: int | None = Field(default=None, ge=0)

    model_config = ConfigDict(extra="forbid")


class NoteResponse(BaseModel):
    id: str
    title: str
    description: str
    topics_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
