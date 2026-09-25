"""Audit dependencies for FastAPI."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.mariadb import get_db
from app.modules.auth.dependencies import get_current_user, get_current_active_user
from app.modules.auth.models import User
from app.modules.audit.services import AuditService


async def get_audit_service(session: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(session)


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin required",
        )
    return current_user