"""TOTP repository for auth module."""
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import TotpSecret


class TotpRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, totp: TotpSecret) -> TotpSecret:
        self.session.add(totp)
        await self.session.flush()
        await self.session.refresh(totp)
        return totp

    async def get_by_user_id(self, user_id: int) -> Optional[TotpSecret]:
        result = await self.session.execute(
            select(TotpSecret).where(TotpSecret.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, totp: TotpSecret) -> TotpSecret:
        await self.session.flush()
        await self.session.refresh(totp)
        return totp

    async def delete(self, user_id: int) -> None:
        await self.session.execute(
            delete(TotpSecret).where(TotpSecret.user_id == user_id)
        )
        await self.session.flush()