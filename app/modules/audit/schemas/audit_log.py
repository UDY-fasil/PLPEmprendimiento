"""AuditLog schemas for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    user_id: int | None = None
    action: str
    entity: str | None = None
    entity_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = {}


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: int | None
    action: str
    entity: str | None
    entity_id: int | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict[str, Any]
    created_at: datetime