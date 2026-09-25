"""Auth API routers with real implementations."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.mariadb import get_db
from app.core.rate_limiter import limiter
from app.modules.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_auth_service,
    get_user_service,
    require_roles,
)
from app.modules.auth.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse as TokenResponseSchema,
    RefreshRequest,
    LogoutRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TotpVerifyRequest,
    TotpEnableResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
    UserPublicResponse,
    UserListResponse,
    SetUserRolesRequest,
)
from app.modules.auth.schemas.role import RoleRead
from app.modules.auth.repositories import RoleRepository
from app.modules.auth.services import AuthService, UserService
from app.modules.auth.models import User


# Auth router
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])


@auth_router.post("/register", response_model=UserPublicResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Registrar nuevo usuario."""
    try:
        user = await auth_service.register(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            phone=data.phone,
            city=data.city,
        )
        return UserPublicResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login", response_model=TokenResponseSchema)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Iniciar sesión."""
    try:
        user, access_token, refresh_token = await auth_service.authenticate(
            email=data.email,
            password=data.password,
            totp_code=data.totp_code,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(
    data: RefreshRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refrescar token de acceso."""
    try:
        access_token, refresh_token = await auth_service.refresh_tokens(
            refresh_token=data.refresh_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Cerrar sesión (revocar refresh token)."""
    await auth_service.logout(data.refresh_token)


@auth_router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Cerrar sesión en todos los dispositivos."""
    await auth_service.logout_all(current_user.id)


@auth_router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Solicitar restablecimiento de contraseña."""
    token = await auth_service.request_password_reset(data.email)
    if token:
        return {"message": "Reset token sent", "token": token}
    return {"message": "If email exists, reset token sent"}


@auth_router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def confirm_password_reset(
    request: Request,
    data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Confirmar restablecimiento de contraseña."""
    success = await auth_service.confirm_password_reset(data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return {"message": "Password reset successful"}


# 2FA TOTP endpoints
@auth_router.post("/2fa/enable", response_model=TotpEnableResponse)
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Habilitar 2FA TOTP."""
    if current_user.totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA already enabled")
    
    secret, backup_codes = await auth_service.enable_totp(current_user.id)
    uri = await auth_service.get_totp_uri(current_user.id)
    
    return TotpEnableResponse(
        secret=secret,
        uri=uri or "",
        backup_codes=backup_codes,
    )


@auth_router.post("/2fa/verify", status_code=status.HTTP_200_OK)
async def verify_2fa(
    data: TotpVerifyRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verificar código TOTP."""
    if not current_user.totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA not enabled")
    
    valid = await auth_service.verify_totp(current_user.id, data.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
    
    return {"valid": True}


@auth_router.post("/2fa/disable", status_code=status.HTTP_200_OK)
async def disable_2fa(
    data: TotpVerifyRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Deshabilitar 2FA TOTP."""
    if not current_user.totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA not enabled")
    
    success = await auth_service.disable_totp(current_user.id, data.code)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
    
    return {"message": "2FA disabled"}


@auth_router.get("/2fa/uri")
async def get_2fa_uri(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Obtener URI para configurar app autenticadora."""
    if not current_user.totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA not enabled")
    
    uri = await auth_service.get_totp_uri(current_user.id)
    return {"uri": uri}


# User router
user_router = APIRouter(prefix="/users", tags=["Usuarios"])


@user_router.get("/me", response_model=UserPublicResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Obtener usuario actual."""
    return UserPublicResponse.model_validate(current_user)


@user_router.patch("/me", response_model=UserPublicResponse)
async def update_me(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Actualizar perfil del usuario actual."""
    user = await user_service.update_profile(
        user_id=current_user.id,
        full_name=data.full_name,
        phone=data.phone,
        city=data.city,
    )
    return UserPublicResponse.model_validate(user)


@user_router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Cambiar contraseña del usuario actual."""
    success = await user_service.change_password(
        user_id=current_user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect")
    return {"message": "Password changed successfully"}


@user_router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Obtener usuario por ID (solo admin)."""
    user = await user_service.get_user_public(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@user_router.get("", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Listar usuarios (solo admin)."""
    skip = (page - 1) * page_size
    users = await user_service.list_users(skip=skip, limit=page_size)
    total = await user_service.user_repo.count_users()
    
    return UserListResponse(
        users=[UserPublicResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@user_router.post("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Desactivar usuario (solo admin)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")
    
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deactivated"}


@user_router.post("/{user_id}/activate", status_code=status.HTTP_200_OK)
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Activar usuario (solo admin)."""
    success = await user_service.activate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User activated"}


@user_router.post("/{user_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Suspender usuario (solo admin)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot suspend yourself")
    
    success = await user_service.suspend_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User suspended"}


# Role router
role_router = APIRouter(prefix="/roles", tags=["Roles"])


@user_router.put("/{user_id}/roles", response_model=UserPublicResponse)
async def set_user_roles(
    user_id: int,
    data: SetUserRolesRequest,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Asignar los roles de un usuario (solo admin)."""
    user = await user_service.set_roles(user_id, data.roles)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserPublicResponse.model_validate(user)


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """Eliminar un usuario (solo admin)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@role_router.get("", response_model=List[RoleRead])
async def list_roles(
    current_user: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
):
    """Listar roles del sistema (solo admin)."""
    roles = await RoleRepository(session).list_roles()
    return [RoleRead.model_validate(r) for r in roles]