"""Auth request/response schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    city: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class TotpEnableResponse(BaseModel):
    secret: str
    uri: str
    backup_codes: List[str]


class TotpVerifyRequest(BaseModel):
    code: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    city: Optional[str] = Field(default=None, max_length=100)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPublicResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    city: Optional[str]
    status: str
    totp_enabled: bool
    roles: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_names(cls, v):
        if not v:
            return []
        if hasattr(v, "__iter__") and not isinstance(v, str):
            first = next(iter(v), None)
            if first is not None and hasattr(first, "name"):
                return [r.name for r in v]
        return v


class UserListResponse(BaseModel):
    users: List[UserPublicResponse]
    total: int
    page: int
    page_size: int