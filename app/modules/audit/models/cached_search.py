"""CachedSearch model for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class CachedSearch(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    query_hash: str
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    results: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}