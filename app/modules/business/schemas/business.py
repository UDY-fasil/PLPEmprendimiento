"""Business schemas for business module."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BusinessCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    category_ids: list[int] = Field(default_factory=list)


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    logo_url: str | None = None
    category_ids: list[int] | None = None


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    name: str
    description: str | None
    city: str | None
    status: str
    created_at: datetime