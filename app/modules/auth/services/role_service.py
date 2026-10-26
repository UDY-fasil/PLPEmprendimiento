"""Role and Permission service for RBAC business logic."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repositories import RoleRepository, PermissionRepository
from app.modules.auth.models import Role, Permission
from app.modules.auth.schemas.role import RoleCreate, RoleRead, PermissionRead


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)
        self.permission_repo = PermissionRepository(session)

    async def create_role(self, name: str, description: Optional[str] = None) -> Role:
        existing = await self.role_repo.get_by_name(name)
        if existing:
            raise ValueError("Role already exists")

        role = Role(name=name, description=description)
        return await self.role_repo.create(role)

    async def get_role(self, role_id: int) -> Optional[Role]:
        return await self.role_repo.get_by_id(role_id)

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        return await self.role_repo.get_by_name(name)

    async def list_roles(self, skip: int = 0, limit: int = 50) -> List[Role]:
        return await self.role_repo.list_roles(skip, limit)

    async def update_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Role]:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            return None

        if name is not None:
            existing = await self.role_repo.get_by_name(name)
            if existing and existing.id != role_id:
                raise ValueError("Role name already exists")
            role.name = name
        if description is not None:
            role.description = description

        return await self.role_repo.update(role)

    async def delete_role(self, role_id: int) -> bool:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            return False
        await self.role_repo.delete(role)
        await self.session.commit()
        return True

    async def assign_permission(self, role_id: int, permission_code: str) -> bool:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            return False

        permission = await self.permission_repo.get_by_code(permission_code)
        if not permission:
            return False

        await self.role_repo.assign_permission(role_id, permission.id)
        await self.session.commit()
        return True

    async def remove_permission(self, role_id: int, permission_code: str) -> bool:
        permission = await self.permission_repo.get_by_code(permission_code)
        if not permission:
            return False

        await self.role_repo.remove_permission(role_id, permission.id)
        await self.session.commit()
        return True

    async def create_permission(self, code: str, description: Optional[str] = None) -> Permission:
        existing = await self.permission_repo.get_by_code(code)
        if existing:
            raise ValueError("Permission already exists")

        permission = Permission(code=code, description=description)
        return await self.permission_repo.create(permission)

    async def list_permissions(self) -> List[Permission]:
        return await self.permission_repo.list_permissions()