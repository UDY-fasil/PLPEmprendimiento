"""CachedSearch schemas for audit module."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class CachedSearchCreate(BaseModel):
    query_hash: str
    query: str
    filters: dict[str, Any] = {}
    results: list[dict[str, Any]] = []


class CachedSearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    query_hash: str
    query: str
    filters: dict[str, Any]
    results: list[dict[str, Any]]
    created_at: datetime