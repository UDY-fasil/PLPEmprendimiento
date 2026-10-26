"""Contact request schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ContactRequestCreate(BaseModel):
    business_id: Optional[int] = None
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    message: Optional[str] = None


class ContactRequestResponse(BaseModel):
    id: int
    business_id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    message: Optional[str]
    status: str
    created_at: datetime
    handled_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ContactRequestListResponse(BaseModel):
    requests: List[ContactRequestResponse]
    total: int
    page: int
    page_size: int


class ContactRequestStatusUpdate(BaseModel):
    status: str
