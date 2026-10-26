"""Session repository for auth module."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import Session


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, session_obj: Session) -> Session:
        self.session.add(session_obj)
        await self.session.flush()
        await self.session.refresh(session_obj)
        return session_obj

    async def get_by_id(self, session_id: int) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_refresh_token_hash(self, token_hash: str) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(Session.refresh_token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: int) -> List[Session]:
        result = await self.session.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
        )
        return result.scalars().all()

    async def revoke(self, session_obj: Session) -> None:
        session_obj.revoked = True
        await self.session.flush()

    async def revoke_all_user_sessions(self, user_id: int) -> None:
        await self.session.execute(
            delete(Session).where(Session.user_id == user_id, Session.revoked == False)
        )
        await self.session.flush()

    async def delete_expired(self) -> int:
        result = await self.session.execute(
            delete(Session).where(Session.expires_at < datetime.utcnow())
        )
        return result.rowcount

    async def cleanup_old_revoked(self, days: int = 30) -> int:
        cutoff = datetime.utcnow()
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)
        result = await self.session.execute(
            delete(Session).where(Session.revoked == True, Session.created_at < cutoff)
        )
        return result.rowcount