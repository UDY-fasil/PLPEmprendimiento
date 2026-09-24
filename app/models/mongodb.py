from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


# =========================================================
# AUDIT LOGS
# =========================================================
class AuditLog(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: int | None = None
    action: str                       # login, logout, create, update, delete...
    entity: str | None = None         # users, businesses, products...
    entity_id: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


# =========================================================
# ACTIVITY EVENTS (TTL 180 días)
# =========================================================
class ActivityEvent(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: int | None = None
    event_type: str                   # visit, search, click, view
    entity: str | None = None
    entity_id: int | None = None
    query: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


# =========================================================
# NOTIFICATIONS HISTORY
# =========================================================
class NotificationHistory(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: int
    type: str                         # inquiry, approval, rejection, system
    title: str
    message: str
    read: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


# =========================================================
# CACHED SEARCHES (TTL 24 horas)
# =========================================================
class CachedSearch(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    query_hash: str
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    results: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}