"""Auth dependencies for FastAPI."""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.mariadb import get_db
from app.core.security import decode_token, JWTError
from app.modules.auth.repositories import UserRepository, SessionRepository, UserRoleRepository
from app.modules.auth.models import User, UserStatus
from app.modules.auth.services import AuthService, UserService


security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        return None

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user or user.status != UserStatus.ACTIVE or user.deleted_at:
        return None

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user or user.status != UserStatus.ACTIVE or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_permissions(*permission_codes: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> User:
        user_role_repo = UserRoleRepository(session)
        
        for code in permission_codes:
            has_perm = False
            for role in current_user.roles:
                for perm in role.permissions:
                    if perm.code == code:
                        has_perm = True
                        break
                if has_perm:
                    break
            
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {code}",
                )
        
        return current_user
    
    return permission_checker


def require_roles(*role_names: str):
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_roles = {role.name for role in current_user.roles}
        
        if not any(role in user_roles for role in role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {', '.join(role_names)}",
            )
        
        return current_user
    
    return role_checker


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)