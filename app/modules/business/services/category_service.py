"""Category service for business logic."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import CategoryRepository
from app.modules.business.models import Category
from app.modules.business.schemas.category import CategoryCreate, CategoryRead


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(self, data: CategoryCreate) -> Category:
        existing = await self.category_repo.get_by_name(data.name)
        if existing:
            raise ValueError("Category already exists")

        category = Category(
            name=data.name,
            description=data.description,
            icon=data.icon,
            active=True,
        )
        category = await self.category_repo.create(category)
        await self.session.commit()
        return category

    async def get_category(self, category_id: int) -> Optional[Category]:
        return await self.category_repo.get_by_id(category_id)

    async def list_categories(
        self,
        page: int = 1,
        page_size: int = 50,
        active_only: bool = True,
    ) -> tuple[List[Category], int]:
        skip = (page - 1) * page_size
        categories = await self.category_repo.list_categories(
            skip=skip,
            limit=page_size,
            active_only=active_only,
        )
        total = await self.category_repo.count_categories(active_only=active_only)
        return categories, total

    async def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Optional[Category]:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return None

        if name is not None:
            existing = await self.category_repo.get_by_name(name)
            if existing and existing.id != category_id:
                raise ValueError("Category name already exists")
            category.name = name
        if description is not None:
            category.description = description
        if icon is not None:
            category.icon = icon
        if active is not None:
            category.active = active

        category = await self.category_repo.update(category)
        await self.session.commit()
        return category

    async def delete_category(self, category_id: int) -> bool:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return False
        await self.category_repo.delete(category)
        await self.session.commit()
        return True