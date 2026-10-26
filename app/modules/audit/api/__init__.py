"""Audit API routers with real implementations."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import datetime

from app.modules.auth.dependencies import get_current_user, get_current_active_user
from app.modules.auth.models import User
from app.modules.audit.dependencies import get_audit_service, require_admin
from app.modules.audit.services import AuditService
from app.modules.audit.schemas.api import (
    AuditLogResponse,
    AuditLogListResponse,
    ActivityEventResponse,
    ActivityEventListResponse,
    NotificationResponse,
    NotificationListResponse,
)


# Audit router
audit_router = APIRouter(prefix="/audit", tags=["Auditoría"])


@audit_router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Listar logs de auditoría (solo admin)."""
    logs, total = await audit_service.list_audit_logs(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        entity=entity,
        start_date=start_date,
        end_date=end_date,
    )
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )


@audit_router.get("/activities", response_model=ActivityEventListResponse)
async def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    entity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Listar eventos de actividad (solo admin)."""
    events, total = await audit_service.list_activities(
        page=page,
        page_size=page_size,
        user_id=user_id,
        event_type=event_type,
        entity=entity,
        start_date=start_date,
        end_date=end_date,
    )
    return ActivityEventListResponse(
        events=[ActivityEventResponse.model_validate(event) for event in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@audit_router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Listar notificaciones del usuario actual."""
    notifications, total = await audit_service.list_notifications(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
    )


@audit_router.post("/notifications/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Marcar notificación como leída."""
    success = await audit_service.mark_notification_read(notification_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"message": "Notification marked as read"}


@audit_router.post("/notifications/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Marcar todas las notificaciones como leídas."""
    count = await audit_service.mark_all_notifications_read(current_user.id)
    return {"message": f"{count} notifications marked as read"}


@audit_router.post("/cleanup-searches", status_code=status.HTTP_200_OK)
async def cleanup_expired_searches(
    current_user: User = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Limpiar búsquedas en caché expiradas (solo admin)."""
    count = await audit_service.cleanup_expired_searches()
    return {"message": f"Cleaned up {count} expired cached searches"}