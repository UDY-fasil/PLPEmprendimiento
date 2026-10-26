"""User service for user management business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repositories import UserRepository, RoleRepository, UserRoleRepository, SessionRepository
from app.modules.auth.models import User, UserStatus, Role
from app.modules.auth.schemas.user import UserRegister, UserPublic
from app.modules.auth.schemas.role import RoleCreate, RoleRead
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.user_role_repo = UserRoleRepository(session)
        self.session_repo = SessionRepository(session)

    async def get_user_public(self, user_id: int) -> Optional[UserPublic]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserPublic.model_validate(user)

    async def get_current_user(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def update_profile(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
    ) -> Optional[User]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone
        if city is not None:
            user.city = city

        return await self.user_repo.update(user)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = hash_password(new_password)
        await self.user_repo.update(user)
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()
        return True

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserStatus] = None,
    ) -> List[User]:
        return await self.user_repo.list_users(skip, limit, status)

    async def get_user_roles(self, user_id: int) -> List[Role]:
        return await self.user_role_repo.get_user_roles(user_id)

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        role = await self.role_repo.get_by_name(role_name)
        if not role:
            return False

        await self.user_role_repo.assign_role(user_id, role.id)
        await self.session.commit()
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        role = await self.role_repo.get_by_name(role_name)
        if not role:
            return False

        await self.user_role_repo.remove_role(user_id, role.id)
        await self.session.commit()
        return True

    async def deactivate_user(self, user_id: int) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        user.status = UserStatus.INACTIVE
        await self.user_repo.update(user)
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()
        return True

    async def activate_user(self, user_id: int) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        user.status = UserStatus.ACTIVE
        await self.user_repo.update(user)
        await self.session.commit()
        return True

    async def suspend_user(self, user_id: int) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        user.status = UserStatus.SUSPENDED
        await self.user_repo.update(user)
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()
        return True

    async def delete_user(self, user_id: int) -> bool:
        """Elimina (soft delete) un usuario y revoca sus sesiones."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        user.status = UserStatus.INACTIVE
        user.deleted_at = datetime.utcnow()
        await self.user_repo.update(user)
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()
        return True

    async def set_roles(self, user_id: int, role_names: List[str]) -> Optional[User]:
        """Reemplaza los roles de un usuario por los indicados."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        existing = await self.user_role_repo.get_user_roles(user_id)
        for role in existing:
            await self.user_role_repo.remove_role(user_id, role.id)

        for name in role_names:
            role = await self.role_repo.get_by_name(name)
            if role:
                await self.user_role_repo.assign_role(user_id, role.id)

        await self.session.commit()
        self.session.expire_all()
        return await self.user_repo.get_by_id(user_id)