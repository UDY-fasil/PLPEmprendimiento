"""Audit service for logging business logic."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.repositories import (
    AuditRepository,
    ActivityRepository,
    NotificationRepository,
    CachedSearchRepository,
)
from app.modules.audit.models import AuditLog, ActivityEvent, NotificationHistory, CachedSearch
from app.modules.audit.schemas.audit_log import AuditLogCreate
from app.modules.audit.schemas.activity_event import ActivityEventCreate
from app.modules.audit.schemas.notification import NotificationCreate
from app.modules.audit.schemas.cached_search import CachedSearchCreate


class AuditService:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.audit_repo = AuditRepository()
        self.activity_repo = ActivityRepository()
        self.notification_repo = NotificationRepository()
        self.cached_search_repo = CachedSearchRepository()

    # Audit Logs
    async def log_action(
        self,
        user_id: Optional[int],
        action: str,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        return await self.audit_repo.create(audit_log)

    async def list_audit_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[AuditLog], int]:
        skip = (page - 1) * page_size
        logs = await self.audit_repo.list_logs(
            skip=skip,
            limit=page_size,
            user_id=user_id,
            action=action,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
        )
        total = await self.audit_repo.count_logs(
            user_id=user_id,
            action=action,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
        )
        return logs, total

    # Activity Events
    async def log_activity(
        self,
        user_id: Optional[int],
        event_type: str,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ActivityEvent:
        activity = ActivityEvent(
            user_id=user_id,
            event_type=event_type,
            entity=entity,
            entity_id=entity_id,
            query=query,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        return await self.activity_repo.create(activity)

    async def log_activities_batch(self, activities: List[ActivityEvent]) -> List[ActivityEvent]:
        return await self.activity_repo.create_many(activities)

    async def list_activities(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[ActivityEvent], int]:
        skip = (page - 1) * page_size
        activities = await self.activity_repo.list_events(
            skip=skip,
            limit=page_size,
            user_id=user_id,
            event_type=event_type,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
        )
        total = await self.activity_repo.count_events(
            user_id=user_id,
            event_type=event_type,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
        )
        return activities, total

    # Notifications
    async def create_notification(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NotificationHistory:
        notification = NotificationHistory(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            read=False,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        return await self.notification_repo.create(notification)

    async def list_notifications(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 50,
        unread_only: bool = False,
    ) -> tuple[List[NotificationHistory], int]:
        skip = (page - 1) * page_size
        notifications = await self.notification_repo.list_notifications(
            skip=skip,
            limit=page_size,
            user_id=user_id,
            unread_only=unread_only,
        )
        total = await self.notification_repo.count_notifications(
            user_id=user_id,
            unread_only=unread_only,
        )
        return notifications, total

    async def mark_notification_read(self, notification_id: str) -> bool:
        return await self.notification_repo.mark_as_read(notification_id)

    async def mark_all_notifications_read(self, user_id: int) -> int:
        return await self.notification_repo.mark_all_as_read(user_id)

    # Cached Searches
    async def get_cached_search(self, query_hash: str) -> Optional[CachedSearch]:
        return await self.cached_search_repo.get_valid_by_query_hash(query_hash)

    async def set_cached_search(
        self,
        query_hash: str,
        query: str,
        filters: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> CachedSearch:
        cached = CachedSearch(
            query_hash=query_hash,
            query=query,
            filters=filters,
            results=results,
            created_at=datetime.utcnow(),
        )
        return await self.cached_search_repo.create(cached)

    async def update_cached_search(
        self,
        query_hash: str,
        results: List[Dict[str, Any]],
    ) -> bool:
        return await self.cached_search_repo.update_results(query_hash, results)

    async def cleanup_expired_searches(self) -> int:
        return await self.cached_search_repo.delete_expired()