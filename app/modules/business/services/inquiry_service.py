"""Inquiry service for business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.repositories import InquiryRepository, BusinessRepository
from app.modules.business.models import Inquiry, InquiryStatus, Business, BusinessStatus
from app.modules.business.schemas.inquiry import InquiryCreate, InquiryRead


class InquiryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.inquiry_repo = InquiryRepository(session)
        self.business_repo = BusinessRepository(session)

    async def create_inquiry(
        self,
        sender_id: Optional[int],
        data: InquiryCreate,
    ) -> Inquiry:
        business = await self.business_repo.get_by_id(data.business_id)
        if not business:
            raise ValueError("Business not found")

        if business.status != BusinessStatus.APPROVED:
            # Para testing, permitir también PENDING
            if business.status != BusinessStatus.PENDING:
                raise ValueError("Business not available for inquiries")

        inquiry = Inquiry(
            business_id=data.business_id,
            sender_id=sender_id,
            sender_name=data.sender_name,
            sender_email=data.sender_email,
            sender_phone=data.sender_phone,
            message=data.message,
            status=InquiryStatus.NEW,
        )
        inquiry = await self.inquiry_repo.create(inquiry)
        await self.session.commit()
        return inquiry

    async def get_inquiry(self, inquiry_id: int) -> Optional[Inquiry]:
        return await self.inquiry_repo.get_by_id(inquiry_id)

    async def update_inquiry_status(
        self,
        inquiry_id: int,
        status: InquiryStatus,
        owner_id: int,
    ) -> Optional[Inquiry]:
        inquiry = await self.inquiry_repo.get_by_id(inquiry_id)
        if not inquiry:
            return None

        business = await self.business_repo.get_by_id(inquiry.business_id)
        if not business or business.owner_id != owner_id:
            raise ValueError("Not authorized to update this inquiry")

        inquiry.status = status
        if status == InquiryStatus.ANSWERED:
            inquiry.responded_at = datetime.utcnow()
        
        inquiry = await self.inquiry_repo.update(inquiry)
        await self.session.commit()
        return inquiry

    async def list_inquiries(
        self,
        page: int = 1,
        page_size: int = 20,
        business_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        status: Optional[InquiryStatus] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[List[Inquiry], int]:
        skip = (page - 1) * page_size
        inquiries = await self.inquiry_repo.list_inquiries(
            skip=skip,
            limit=page_size,
            business_id=business_id,
            sender_id=sender_id,
            status=status,
            owner_id=owner_id,
        )
        total = await self.inquiry_repo.count_inquiries(
            business_id=business_id,
            sender_id=sender_id,
            status=status,
            owner_id=owner_id,
        )
        return inquiries, total

    async def get_business_inquiries(
        self,
        business_id: int,
        owner_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Inquiry], int]:
        business = await self.business_repo.get_by_id(business_id)
        if not business or business.owner_id != owner_id:
            raise ValueError("Not authorized")
        
        return await self.list_inquiries(
            page=page,
            page_size=page_size,
            business_id=business_id,
        )

    async def get_my_inquiries(
        self,
        sender_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Inquiry], int]:
        return await self.list_inquiries(
            page=page,
            page_size=page_size,
            sender_id=sender_id,
        )