"""Category repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True,
    ) -> List[Category]:
        query = select(Category)
        if active_only:
            query = query.where(Category.active == True)
        query = query.offset(skip).limit(limit).order_by(Category.name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_categories(self, active_only: bool = True) -> int:
        query = select(func.count(Category.id))
        if active_only:
            query = query.where(Category.active == True)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update(self, category: Category) -> Category:
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.flush()