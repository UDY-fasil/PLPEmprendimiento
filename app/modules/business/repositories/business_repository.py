"""Business repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Business, BusinessStatus, Category, BusinessCategory
from app.modules.business.schemas.business import BusinessCreate, BusinessUpdate


class BusinessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, business: Business) -> Business:
        self.session.add(business)
        await self.session.flush()
        await self.session.refresh(business)
        return business

    async def get_by_id(self, business_id: int) -> Optional[Business]:
        result = await self.session.execute(
            select(Business)
            .options(
                selectinload(Business.categories),
                selectinload(Business.owner),
            )
            .where(Business.id == business_id, Business.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_owner(self, business_id: int) -> Optional[Business]:
        result = await self.session.execute(
            select(Business)
            .options(selectinload(Business.owner))
            .where(Business.id == business_id, Business.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def update(self, business: Business) -> Business:
        await self.session.flush()
        await self.session.refresh(business)
        return business

    async def delete(self, business: Business) -> None:
        from datetime import datetime
        business.deleted_at = datetime.utcnow()
        business.status = BusinessStatus.DELETED
        await self.session.flush()

    async def list_businesses(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BusinessStatus] = None,
        city: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> List[Business]:
        query = select(Business).where(Business.deleted_at.is_(None))
        
        if status:
            query = query.where(Business.status == status)
        if city:
            query = query.where(Business.city.ilike(f"%{city}%"))
        if owner_id:
            query = query.where(Business.owner_id == owner_id)
        if search:
            query = query.where(
                or_(
                    Business.name.ilike(f"%{search}%"),
                    Business.description.ilike(f"%{search}%"),
                )
            )
        if category_id:
            query = query.join(BusinessCategory).where(BusinessCategory.category_id == category_id)
        
        query = query.options(selectinload(Business.categories))
        query = query.offset(skip).limit(limit).order_by(Business.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_businesses(
        self,
        status: Optional[BusinessStatus] = None,
        city: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> int:
        query = select(func.count(Business.id)).where(Business.deleted_at.is_(None))
        
        if status:
            query = query.where(Business.status == status)
        if city:
            query = query.where(Business.city.ilike(f"%{city}%"))
        if owner_id:
            query = query.where(Business.owner_id == owner_id)
        if search:
            query = query.where(
                or_(
                    Business.name.ilike(f"%{search}%"),
                    Business.description.ilike(f"%{search}%"),
                )
            )
        if category_id:
            query = query.join(BusinessCategory).where(BusinessCategory.category_id == category_id)
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_category(self, business_id: int, category_id: int) -> BusinessCategory:
        bc = BusinessCategory(business_id=business_id, category_id=category_id)
        self.session.add(bc)
        await self.session.flush()
        return bc

    async def remove_category(self, business_id: int, category_id: int) -> None:
        result = await self.session.execute(
            select(BusinessCategory).where(
                BusinessCategory.business_id == business_id,
                BusinessCategory.category_id == category_id,
            )
        )
        bc = result.scalar_one_or_none()
        if bc:
            await self.session.delete(bc)
            await self.session.flush()

    async def set_categories(self, business_id: int, category_ids: List[int]) -> None:
        await self.session.execute(
            BusinessCategory.__table__.delete().where(
                BusinessCategory.business_id == business_id
            )
        )
        for cat_id in category_ids:
            bc = BusinessCategory(business_id=business_id, category_id=cat_id)
            self.session.add(bc)
        await self.session.flush()