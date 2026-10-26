"""Favorite service for business logic."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import FavoriteRepository, BusinessRepository, ProductRepository
from app.modules.business.models import Favorite, Business, Product
from app.modules.business.schemas.favorite import FavoriteCreate, FavoriteRead


class FavoriteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.favorite_repo = FavoriteRepository(session)
        self.business_repo = BusinessRepository(session)
        self.product_repo = ProductRepository(session)

    async def add_favorite(
        self,
        user_id: int,
        data: FavoriteCreate,
    ) -> Favorite:
        if not data.business_id and not data.product_id:
            raise ValueError("Either business_id or product_id is required")

        if data.business_id:
            business = await self.business_repo.get_by_id(data.business_id)
            if not business:
                raise ValueError("Business not found")

        if data.product_id:
            product = await self.product_repo.get_by_id(data.product_id)
            if not product:
                raise ValueError("Product not found")

        existing = await self.favorite_repo.get_user_favorite(
            user_id=user_id,
            business_id=data.business_id,
            product_id=data.product_id,
        )
        if existing:
            raise ValueError("Already in favorites")

        favorite = Favorite(
            user_id=user_id,
            business_id=data.business_id,
            product_id=data.product_id,
        )
        favorite = await self.favorite_repo.create(favorite)
        await self.session.commit()
        return favorite

    async def remove_favorite(
        self,
        user_id: int,
        business_id: Optional[int] = None,
        product_id: Optional[int] = None,
    ) -> bool:
        favorite = await self.favorite_repo.get_user_favorite(
            user_id=user_id,
            business_id=business_id,
            product_id=product_id,
        )
        if not favorite:
            return False

        await self.favorite_repo.delete(favorite)
        await self.session.commit()
        return True

    async def list_favorites(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Favorite], int]:
        skip = (page - 1) * page_size
        favorites = await self.favorite_repo.list_favorites(
            user_id=user_id,
            skip=skip,
            limit=page_size,
        )
        total = await self.favorite_repo.count_favorites(user_id)
        return favorites, total

    async def is_favorite(
        self,
        user_id: int,
        business_id: Optional[int] = None,
        product_id: Optional[int] = None,
    ) -> bool:
        favorite = await self.favorite_repo.get_user_favorite(
            user_id=user_id,
            business_id=business_id,
            product_id=product_id,
        )
        return favorite is not None