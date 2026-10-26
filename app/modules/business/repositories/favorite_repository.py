"""Favorite repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Favorite


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, favorite: Favorite) -> Favorite:
        self.session.add(favorite)
        await self.session.flush()
        await self.session.refresh(favorite)
        return favorite

    async def get_by_id(self, favorite_id: int) -> Optional[Favorite]:
        result = await self.session.execute(
            select(Favorite).where(Favorite.id == favorite_id)
        )
        return result.scalar_one_or_none()

    async def get_user_favorite(
        self,
        user_id: int,
        business_id: Optional[int] = None,
        product_id: Optional[int] = None,
    ) -> Optional[Favorite]:
        query = select(Favorite).where(Favorite.user_id == user_id)
        if business_id:
            query = query.where(Favorite.business_id == business_id)
        if product_id:
            query = query.where(Favorite.product_id == product_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_favorites(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Favorite]:
        result = await self.session.execute(
            select(Favorite)
            .options(
                selectinload(Favorite.business),
                selectinload(Favorite.product),
            )
            .where(Favorite.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Favorite.created_at.desc())
        )
        return result.scalars().all()

    async def count_favorites(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        return result.scalar() or 0

    async def delete(self, favorite: Favorite) -> None:
        await self.session.delete(favorite)
        await self.session.flush()