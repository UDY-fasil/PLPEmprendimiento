"""Product service for business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import ProductRepository, BusinessRepository
from app.modules.business.models import Product, Business
from app.modules.business.schemas.product import ProductCreate, ProductUpdate, ProductRead


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.business_repo = BusinessRepository(session)

    async def create_product(
        self,
        business_id: int,
        owner_id: int,
        data: ProductCreate,
        is_admin: bool = False,
    ) -> Product:
        business = await self.business_repo.get_by_id_with_owner(business_id)
        if not business:
            raise ValueError("Business not found")

        if not is_admin and business.owner_id != owner_id:
            raise ValueError("Not authorized to add products to this business")

        product = Product(
            business_id=business_id,
            name=data.name,
            description=data.description,
            price=data.price,
            currency=data.currency or "ARS",
            stock=data.stock,
            image_url=getattr(data, "image_url", None),
            active=True,
        )
        product = await self.product_repo.create(product)
        await self.session.commit()
        return product

    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def get_product_with_business(self, product_id: int) -> Optional[Product]:
        return await self.product_repo.get_by_id_with_business(product_id)

    async def update_product(
        self,
        product_id: int,
        owner_id: int,
        data: ProductUpdate,
        is_admin: bool = False,
    ) -> Optional[Product]:
        product = await self.product_repo.get_by_id_with_business(product_id)
        if not product:
            return None

        if not is_admin and product.business.owner_id != owner_id:
            raise ValueError("Not authorized to update this product")

        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.currency is not None:
            product.currency = data.currency
        if data.stock is not None:
            product.stock = data.stock
        if data.image_url is not None:
            product.image_url = data.image_url
        if data.active is not None:
            product.active = data.active

        product = await self.product_repo.update(product)
        await self.session.commit()
        return product

    async def delete_product(self, product_id: int, owner_id: int, is_admin: bool = False) -> bool:
        product = await self.product_repo.get_by_id_with_business(product_id)
        if not product:
            return False

        if not is_admin and product.business.owner_id != owner_id:
            raise ValueError("Not authorized to delete this product")

        await self.product_repo.delete(product)
        await self.session.commit()
        return True

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[List[Product], int]:
        skip = (page - 1) * page_size
        products = await self.product_repo.list_products(
            skip=skip,
            limit=page_size,
            business_id=business_id,
            active_only=active_only,
            search=search,
            owner_id=owner_id,
        )
        total = await self.product_repo.count_products(
            business_id=business_id,
            active_only=active_only,
            search=search,
            owner_id=owner_id,
        )
        return products, total