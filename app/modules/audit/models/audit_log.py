"""AuditLog model for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: int | None = None
    action: str
    entity: str | None = None
    entity_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}