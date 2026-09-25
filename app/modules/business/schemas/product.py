"""Product schemas for business module."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    business_id: int
    name: str
    description: str | None = None
    price: float | None = None
    currency: str = "ARS"
    stock: int | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    stock: int | None = None
    image_url: str | None = None
    active: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    business_id: int
    name: str
    description: str | None
    price: float | None
    currency: str
    stock: int | None
    active: bool
    created_at: datetime