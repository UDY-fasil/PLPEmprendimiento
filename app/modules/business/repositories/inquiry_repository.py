"""Inquiry repository for business module."""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.business.models import Inquiry, InquiryStatus
from app.modules.business.models.business import Business


class InquiryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, inquiry: Inquiry) -> Inquiry:
        self.session.add(inquiry)
        await self.session.flush()
        await self.session.refresh(inquiry)
        return inquiry

    async def get_by_id(self, inquiry_id: int) -> Optional[Inquiry]:
        result = await self.session.execute(
            select(Inquiry)
            .options(
                selectinload(Inquiry.business),
            )
            .where(Inquiry.id == inquiry_id)
        )
        return result.scalar_one_or_none()

    async def update(self, inquiry: Inquiry) -> Inquiry:
        await self.session.flush()
        await self.session.refresh(inquiry)
        return inquiry

    async def list_inquiries(
        self,
        skip: int = 0,
        limit: int = 20,
        business_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        status: Optional[InquiryStatus] = None,
        owner_id: Optional[int] = None,
    ) -> List[Inquiry]:
        query = select(Inquiry)

        if owner_id is not None:
            query = query.join(Business, Inquiry.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Inquiry.business_id == business_id)
        if sender_id:
            query = query.where(Inquiry.sender_id == sender_id)
        if status:
            query = query.where(Inquiry.status == status)
        
        query = query.options(selectinload(Inquiry.business))
        query = query.offset(skip).limit(limit).order_by(Inquiry.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_inquiries(
        self,
        business_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        status: Optional[InquiryStatus] = None,
        owner_id: Optional[int] = None,
    ) -> int:
        query = select(func.count(Inquiry.id))

        if owner_id is not None:
            query = query.join(Business, Inquiry.business_id == Business.id).where(
                Business.owner_id == owner_id
            )
        if business_id:
            query = query.where(Inquiry.business_id == business_id)
        if sender_id:
            query = query.where(Inquiry.sender_id == sender_id)
        if status:
            query = query.where(Inquiry.status == status)
        
        result = await self.session.execute(query)
        return result.scalar() or 0