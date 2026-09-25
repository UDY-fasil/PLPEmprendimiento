"""User repository for auth module."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User, UserStatus, Role
from app.core.security import hash_password, verify_password


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email_with_password(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        user.deleted_at = user.updated_at
        await self.session.flush()

    async def verify_password(self, user: User, password: str) -> bool:
        return verify_password(password, user.hashed_password)

    async def set_password(self, user: User, password: str) -> None:
        user.hashed_password = hash_password(password)
        await self.session.flush()

    async def increment_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts += 1
        await self.session.flush()

    async def reset_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()

    async def lock_user(self, user: User, locked_until) -> None:
        user.locked_until = locked_until
        await self.session.flush()

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserStatus] = None,
    ):
        query = select(User).where(User.deleted_at.is_(None))
        if status:
            query = query.where(User.status == status)
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_users(self, status: Optional[UserStatus] = None) -> int:
        query = select(User).where(User.deleted_at.is_(None))
        if status:
            query = query.where(User.status == status)
        result = await self.session.execute(query)
        return len(result.scalars().all())