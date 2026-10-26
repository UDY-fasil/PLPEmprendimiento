"""Auth module schemas package."""
from app.modules.auth.schemas.user import UserRegister, UserLogin, UserPublic
from app.modules.auth.schemas.token import TokenResponse
from app.modules.auth.schemas.role import RoleCreate, RoleRead, PermissionRead
from app.modules.auth.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse as TokenResponseSchema,
    RefreshRequest,
    LogoutRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TotpEnableResponse,
    TotpVerifyRequest,
    UserProfileUpdate,
    ChangePasswordRequest,
    UserPublicResponse,
    UserListResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserPublic",
    "TokenResponse",
    "RoleCreate",
    "RoleRead",
    "PermissionRead",
    "RegisterRequest",
    "LoginRequest",
    "TokenResponseSchema",
    "RefreshRequest",
    "LogoutRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "TotpEnableResponse",
    "TotpVerifyRequest",
    "UserProfileUpdate",
    "ChangePasswordRequest",
    "UserPublicResponse",
    "UserListResponse",
]