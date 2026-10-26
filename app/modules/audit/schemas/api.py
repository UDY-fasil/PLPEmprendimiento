"""Audit API request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[int]
    action: str
    entity: Optional[str]
    entity_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class ActivityEventResponse(BaseModel):
    id: str
    user_id: Optional[int]
    event_type: str
    entity: Optional[str]
    entity_id: Optional[int]
    query: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityEventListResponse(BaseModel):
    events: List[ActivityEventResponse]
    total: int
    page: int
    page_size: int


class NotificationResponse(BaseModel):
    id: str
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int


class CachedSearchResponse(BaseModel):
    id: str
    query_hash: str
    query: str
    filters: Dict[str, Any]
    results: List[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}