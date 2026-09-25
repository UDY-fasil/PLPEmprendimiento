"""Notification schemas for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    user_id: int
    type: str
    title: str
    message: str
    metadata: dict[str, Any] = {}


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    metadata: dict[str, Any]
    created_at: datetime