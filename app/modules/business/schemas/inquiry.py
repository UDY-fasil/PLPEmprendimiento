"""Inquiry schemas for business module."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class InquiryCreate(BaseModel):
    business_id: int
    sender_name: str
    sender_email: EmailStr
    sender_phone: str | None = None
    message: str


class InquiryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    business_id: int
    sender_id: int | None
    sender_name: str
    sender_email: str
    sender_phone: str | None
    message: str
    status: str
    created_at: datetime
    responded_at: datetime | None