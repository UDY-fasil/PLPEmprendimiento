"""ActivityEvent schemas for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class ActivityEventCreate(BaseModel):
    user_id: int | None = None
    event_type: str
    entity: str | None = None
    entity_id: int | None = None
    query: str | None = None
    metadata: dict[str, Any] = {}


class ActivityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: int | None
    event_type: str
    entity: str | None
    entity_id: int | None
    query: str | None
    metadata: dict[str, Any]
    created_at: datetime