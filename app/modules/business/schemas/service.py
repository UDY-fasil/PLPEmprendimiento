"""Service schemas for business module."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    business_id: int
    name: str
    description: str | None = None
    price: float | None = None
    currency: str = "ARS"
    duration_minutes: int | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    duration_minutes: int | None = None
    image_url: str | None = None
    active: bool | None = None


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    business_id: int
    name: str
    description: str | None
    price: float | None
    currency: str
    duration_minutes: int | None
    active: bool
    created_at: datetime