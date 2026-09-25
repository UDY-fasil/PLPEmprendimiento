"""Business service for business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import BusinessRepository, CategoryRepository
from app.modules.business.models import Business, BusinessStatus, Category
from app.modules.business.schemas.business import BusinessCreate, BusinessUpdate, BusinessRead
from app.modules.auth.models import User


class BusinessService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.business_repo = BusinessRepository(session)
        self.category_repo = CategoryRepository(session)

    async def create_business(
        self,
        owner_id: int,
        data: BusinessCreate,
    ) -> Business:
        owner = await self.session.get(User, owner_id)
        if not owner:
            raise ValueError("Owner not found")

        for cat_id in data.category_ids:
            cat = await self.category_repo.get_by_id(cat_id)
            if not cat:
                raise ValueError(f"Category {cat_id} not found")

        business = Business(
            owner_id=owner_id,
            name=data.name,
            description=data.description,
            address=data.address,
            city=data.city,
            latitude=data.latitude,
            longitude=data.longitude,
            phone=data.phone,
            email=data.email,
            website=data.website,
            status=BusinessStatus.PENDING,
        )
        business = await self.business_repo.create(business)

        if data.category_ids:
            await self.business_repo.set_categories(business.id, data.category_ids)

        await self.session.commit()
        await self.session.refresh(business, ["categories"])
        return business

    async def get_business(self, business_id: int) -> Optional[Business]:
        return await self.business_repo.get_by_id(business_id)

    async def get_business_with_owner(self, business_id: int) -> Optional[Business]:
        return await self.business_repo.get_by_id_with_owner(business_id)

    async def update_business(
        self,
        business_id: int,
        owner_id: int,
        data: BusinessUpdate,
    ) -> Optional[Business]:
        business = await self.business_repo.get_by_id_with_owner(business_id)
        if not business:
            return None

        if business.owner_id != owner_id:
            raise ValueError("Not authorized to update this business")

        if data.name is not None:
            business.name = data.name
        if data.description is not None:
            business.description = data.description
        if data.address is not None:
            business.address = data.address
        if data.city is not None:
            business.city = data.city
        if data.latitude is not None:
            business.latitude = data.latitude
        if data.longitude is not None:
            business.longitude = data.longitude
        if data.phone is not None:
            business.phone = data.phone
        if data.email is not None:
            business.email = data.email
        if data.website is not None:
            business.website = data.website
        if data.logo_url is not None:
            business.logo_url = data.logo_url
        if data.category_ids is not None:
            for cat_id in data.category_ids:
                cat = await self.category_repo.get_by_id(cat_id)
                if not cat:
                    raise ValueError(f"Category {cat_id} not found")
            await self.business_repo.set_categories(business_id, data.category_ids)

        business = await self.business_repo.update(business)
        await self.session.commit()
        await self.session.refresh(business, ["categories"])
        return business

    async def delete_business(self, business_id: int, owner_id: int) -> bool:
        business = await self.business_repo.get_by_id_with_owner(business_id)
        if not business:
            return False

        if business.owner_id != owner_id:
            raise ValueError("Not authorized to delete this business")

        await self.business_repo.delete(business)
        await self.session.commit()
        return True

    async def list_businesses(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[BusinessStatus] = None,
        city: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[List[Business], int]:
        skip = (page - 1) * page_size
        businesses = await self.business_repo.list_businesses(
            skip=skip,
            limit=page_size,
            status=status,
            city=city,
            category_id=category_id,
            search=search,
            owner_id=owner_id,
        )
        total = await self.business_repo.count_businesses(
            status=status,
            city=city,
            category_id=category_id,
            search=search,
            owner_id=owner_id,
        )
        return businesses, total

    async def approve_business(self, business_id: int) -> Optional[Business]:
        business = await self.business_repo.get_by_id(business_id)
        if not business:
            return None

        business.status = BusinessStatus.APPROVED
        await self.business_repo.update(business)
        await self.session.commit()
        return business

    async def suspend_business(self, business_id: int) -> Optional[Business]:
        business = await self.business_repo.get_by_id(business_id)
        if not business:
            return None

        business.status = BusinessStatus.SUSPENDED
        await self.business_repo.update(business)
        await self.session.commit()
        return business

    async def get_owner_businesses(self, owner_id: int) -> List[Business]:
        return await self.business_repo.list_businesses(owner_id=owner_id)