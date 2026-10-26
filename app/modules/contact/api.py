"""Contact request API (público para crear, admin para gestionar)."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.mariadb import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.contact.models import ContactRequest, ContactRequestStatus
from app.modules.contact.schemas import (
    ContactRequestCreate,
    ContactRequestListResponse,
    ContactRequestResponse,
    ContactRequestStatusUpdate,
)

contact_router = APIRouter(prefix="/contact-requests", tags=["Contactos"])


def _is_admin(user: User) -> bool:
    return "admin" in {role.name for role in user.roles}


@contact_router.post("", response_model=ContactRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_request(
    data: ContactRequestCreate,
    session: AsyncSession = Depends(get_db),
):
    """Crear una solicitud de contacto (no requiere autenticación)."""
    request = ContactRequest(
        business_id=data.business_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        message=data.message,
        status=ContactRequestStatus.NEW,
    )
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return ContactRequestResponse.model_validate(request)


@contact_router.get("", response_model=ContactRequestListResponse)
async def list_contact_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Listar solicitudes de contacto (solo admin)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

    query = select(ContactRequest)
    count_query = select(func.count(ContactRequest.id))
    if status_filter:
        query = query.where(ContactRequest.status == status_filter)
        count_query = count_query.where(ContactRequest.status == status_filter)

    query = query.order_by(ContactRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    requests = result.scalars().all()
    total = (await session.execute(count_query)).scalar() or 0

    return ContactRequestListResponse(
        requests=[ContactRequestResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
    )


@contact_router.patch("/{request_id}", response_model=ContactRequestResponse)
async def update_contact_request(
    request_id: int,
    data: ContactRequestStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Actualizar el estado de una solicitud (solo admin)."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

    request = await session.get(ContactRequest, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")

    try:
        new_status = ContactRequestStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    request.status = new_status
    if new_status == ContactRequestStatus.CONTACTED:
        request.handled_at = datetime.utcnow()

    await session.commit()
    await session.refresh(request)
    return ContactRequestResponse.model_validate(request)
