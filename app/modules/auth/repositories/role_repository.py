"""Role and Permission repository for auth module."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import Role, Permission, UserRole, RolePermission


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def list_roles(self, skip: int = 0, limit: int = 50) -> List[Role]:
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
            .order_by(Role.name)
        )
        return result.scalars().all()

    async def update(self, role: Role) -> Role:
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
        await self.session.flush()

    async def assign_permission(self, role_id: int, permission_id: int) -> RolePermission:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(rp)
        await self.session.flush()
        return rp

    async def remove_permission(self, role_id: int, permission_id: int) -> None:
        result = await self.session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        rp = result.scalar_one_or_none()
        if rp:
            await self.session.delete(rp)
            await self.session.flush()


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission

    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        result = await self.session.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    async def list_permissions(self) -> List[Permission]:
        result = await self.session.execute(
            select(Permission).order_by(Permission.code)
        )
        return result.scalars().all()


class UserRoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def assign_role(self, user_id: int, role_id: int) -> UserRole:
        ur = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(ur)
        await self.session.flush()
        return ur

    async def remove_role(self, user_id: int, role_id: int) -> None:
        result = await self.session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        ur = result.scalar_one_or_none()
        if ur:
            await self.session.delete(ur)
            await self.session.flush()

    async def get_user_roles(self, user_id: int) -> List[Role]:
        result = await self.session.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def has_role(self, user_id: int, role_name: str) -> bool:
        result = await self.session.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Role.name == role_name)
        )
        return result.scalar_one_or_none() is not None