"""Business dependencies for FastAPI."""
from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.mariadb import get_db
from app.modules.auth.dependencies import get_current_user, get_current_active_user
from app.modules.auth.models import User
from app.modules.business.services import (
    BusinessService,
    CategoryService,
    ProductService,
    ServiceService,
    FavoriteService,
    InquiryService,
)
from app.modules.business.models import Business, BusinessStatus, InquiryStatus


async def get_business_service(session: AsyncSession = Depends(get_db)) -> BusinessService:
    return BusinessService(session)


async def get_category_service(session: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(session)


async def get_product_service(session: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(session)


async def get_service_service(session: AsyncSession = Depends(get_db)) -> ServiceService:
    return ServiceService(session)


async def get_favorite_service(session: AsyncSession = Depends(get_db)) -> FavoriteService:
    return FavoriteService(session)


async def get_inquiry_service(session: AsyncSession = Depends(get_db)) -> InquiryService:
    return InquiryService(session)


async def get_business_or_404(
    business_id: int,
    business_service: BusinessService = Depends(get_business_service),
) -> Business:
    business = await business_service.get_business(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


async def get_business_with_owner_or_404(
    business_id: int,
    business_service: BusinessService = Depends(get_business_service),
) -> Business:
    business = await business_service.get_business_with_owner(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


def require_business_owner(
    business: Business = Depends(get_business_with_owner_or_404),
    current_user: User = Depends(get_current_active_user),
) -> Business:
    if business.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the business owner",
        )
    return business


def require_business_owner_or_admin(
    business: Business = Depends(get_business_with_owner_or_404),
    current_user: User = Depends(get_current_active_user),
) -> Business:
    user_roles = {role.name for role in current_user.roles}
    if business.owner_id != current_user.id and "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return business