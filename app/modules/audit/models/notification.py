"""NotificationHistory model for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class NotificationHistory(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: int
    type: str
    title: str
    message: str
    read: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}