"""Favorite schemas for business module."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    business_id: int | None = None
    product_id: int | None = None


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    business_id: int | None
    product_id: int | None
    created_at: datetime