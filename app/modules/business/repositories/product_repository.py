"""Product repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Product
from app.modules.business.models.business import Business
from app.modules.business.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.business))
            .where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_business(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.business))
            .where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def update(self, product: Product) -> Product:
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        from datetime import datetime
        product.deleted_at = datetime.utcnow()
        product.active = False
        await self.session.flush()

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 20,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> List[Product]:
        query = select(Product).where(Product.deleted_at.is_(None))

        if owner_id is not None:
            query = query.join(Business, Product.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Product.business_id == business_id)
        if active_only:
            query = query.where(Product.active == True)
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )
        
        query = query.options(selectinload(Product.business))
        query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_products(
        self,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> int:
        query = select(func.count(Product.id)).where(Product.deleted_at.is_(None))

        if owner_id is not None:
            query = query.join(Business, Product.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Product.business_id == business_id)
        if active_only:
            query = query.where(Product.active == True)
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )
        
        result = await self.session.execute(query)
        return result.scalar() or 0