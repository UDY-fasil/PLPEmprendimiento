"""Password reset repository for auth module."""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import PasswordReset
from app.core.security import hash_password, verify_password


class PasswordResetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, reset: PasswordReset) -> PasswordReset:
        self.session.add(reset)
        await self.session.flush()
        await self.session.refresh(reset)
        return reset

    async def get_by_token_hash(self, token_hash: str) -> Optional[PasswordReset]:
        result = await self.session.execute(
            select(PasswordReset).where(PasswordReset.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_valid_by_token_hash(self, token_hash: str) -> Optional[PasswordReset]:
        result = await self.session.execute(
            select(PasswordReset).where(
                PasswordReset.token_hash == token_hash,
                PasswordReset.used == False,
                PasswordReset.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, reset: PasswordReset) -> None:
        reset.used = True
        await self.session.flush()

    async def delete_expired(self) -> int:
        result = await self.session.execute(
            delete(PasswordReset).where(
                (PasswordReset.expires_at < datetime.utcnow()) | (PasswordReset.used == True)
            )
        )
        return result.rowcount