from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ================= AUTH =================
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ================= USER =================
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str | None
    city: str | None
    created_at: datetime


# ================= BUSINESS =================
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


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    city: str | None
    status: str


# ================= PRODUCT =================
class ProductCreate(BaseModel):
    business_id: int
    name: str
    description: str | None = None
    price: float | None = None
    currency: str = "ARS"
    stock: int | None = None


# ================= SERVICE =================
class ServiceCreate(BaseModel):
    business_id: int
    name: str
    description: str | None = None
    price: float | None = None
    duration_minutes: int | None = None


# ================= INQUIRY =================
class InquiryCreate(BaseModel):
    business_id: int
    sender_name: str
    sender_email: EmailStr
    sender_phone: str | None = None
    message: str