"""Service service for business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import ServiceRepository, BusinessRepository
from app.modules.business.models import Service, Business
from app.modules.business.schemas.service import ServiceCreate, ServiceUpdate, ServiceRead


class ServiceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service_repo = ServiceRepository(session)
        self.business_repo = BusinessRepository(session)

    async def create_service(
        self,
        business_id: int,
        owner_id: int,
        data: ServiceCreate,
        is_admin: bool = False,
    ) -> Service:
        business = await self.business_repo.get_by_id_with_owner(business_id)
        if not business:
            raise ValueError("Business not found")

        if not is_admin and business.owner_id != owner_id:
            raise ValueError("Not authorized to add services to this business")

        service = Service(
            business_id=business_id,
            name=data.name,
            description=data.description,
            price=data.price,
            currency=data.currency or "ARS",
            duration_minutes=data.duration_minutes,
            active=True,
        )
        service = await self.service_repo.create(service)
        await self.session.commit()
        return service

    async def get_service(self, service_id: int) -> Optional[Service]:
        return await self.service_repo.get_by_id(service_id)

    async def get_service_with_business(self, service_id: int) -> Optional[Service]:
        return await self.service_repo.get_by_id_with_business(service_id)

    async def update_service(
        self,
        service_id: int,
        owner_id: int,
        data: ServiceUpdate,
        is_admin: bool = False,
    ) -> Optional[Service]:
        service = await self.service_repo.get_by_id_with_business(service_id)
        if not service:
            return None

        if not is_admin and service.business.owner_id != owner_id:
            raise ValueError("Not authorized to update this service")

        if data.name is not None:
            service.name = data.name
        if data.description is not None:
            service.description = data.description
        if data.price is not None:
            service.price = data.price
        if data.currency is not None:
            service.currency = data.currency
        if data.duration_minutes is not None:
            service.duration_minutes = data.duration_minutes
        if data.image_url is not None:
            service.image_url = data.image_url
        if data.active is not None:
            service.active = data.active

        service = await self.service_repo.update(service)
        await self.session.commit()
        return service

    async def delete_service(self, service_id: int, owner_id: int, is_admin: bool = False) -> bool:
        service = await self.service_repo.get_by_id_with_business(service_id)
        if not service:
            return False

        if not is_admin and service.business.owner_id != owner_id:
            raise ValueError("Not authorized to delete this service")

        await self.service_repo.delete(service)
        await self.session.commit()
        return True

    async def list_services(
        self,
        page: int = 1,
        page_size: int = 20,
        business_id: Optional[int] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[List[Service], int]:
        skip = (page - 1) * page_size
        services = await self.service_repo.list_services(
            skip=skip,
            limit=page_size,
            business_id=business_id,
            active_only=active_only,
            search=search,
            owner_id=owner_id,
        )
        total = await self.service_repo.count_services(
            business_id=business_id,
            active_only=active_only,
            search=search,
            owner_id=owner_id,
        )
        return services, total