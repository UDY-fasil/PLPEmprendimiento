"""Service repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Service
from app.modules.business.models.business import Business
from app.modules.business.schemas.service import ServiceCreate, ServiceUpdate


class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, service: Service) -> Service:
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def get_by_id(self, service_id: int) -> Optional[Service]:
        result = await self.session.execute(
            select(Service)
            .options(selectinload(Service.business))
            .where(Service.id == service_id, Service.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_business(self, service_id: int) -> Optional[Service]:
        result = await self.session.execute(
            select(Service)
            .options(selectinload(Service.business))
            .where(Service.id == service_id, Service.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def update(self, service: Service) -> Service:
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def delete(self, service: Service) -> None:
        from datetime import datetime
        service.deleted_at = datetime.utcnow()
        service.active = False
        await self.session.flush()

    async def list_services(
        self,
        skip: int = 0,
        limit: int = 20,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> List[Service]:
        query = select(Service).where(Service.deleted_at.is_(None))

        if owner_id is not None:
            query = query.join(Business, Service.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Service.business_id == business_id)
        if active_only:
            query = query.where(Service.active == True)
        if search:
            query = query.where(
                or_(
                    Service.name.ilike(f"%{search}%"),
                    Service.description.ilike(f"%{search}%"),
                )
            )
        
        query = query.options(selectinload(Service.business))
        query = query.offset(skip).limit(limit).order_by(Service.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_services(
        self,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> int:
        query = select(func.count(Service.id)).where(Service.deleted_at.is_(None))

        if owner_id is not None:
            query = query.join(Business, Service.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Service.business_id == business_id)
        if active_only:
            query = query.where(Service.active == True)
        if search:
            query = query.where(
                or_(
                    Service.name.ilike(f"%{search}%"),
                    Service.description.ilike(f"%{search}%"),
                )
            )
        
        result = await self.session.execute(query)
        return result.scalar() or 0