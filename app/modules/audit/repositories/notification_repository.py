"""Notification history repository for MongoDB."""
from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database.mongodb import get_mongo_db
from app.modules.audit.models import NotificationHistory


class NotificationRepository:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_mongo_db()
        return self._db

    @property
    def collection(self):
        return self.db["notifications_history"]

    async def create(self, notification: NotificationHistory) -> NotificationHistory:
        doc = notification.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        notification.id = str(result.inserted_id)
        return notification

    async def get_by_id(self, notification_id: str) -> Optional[NotificationHistory]:
        from bson import ObjectId
        doc = await self.collection.find_one({"_id": ObjectId(notification_id)})
        if doc:
            return NotificationHistory.model_validate(doc)
        return None

    async def list_notifications(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        unread_only: bool = False,
    ) -> List[NotificationHistory]:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if unread_only:
            query["read"] = False
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [NotificationHistory.model_validate(doc) for doc in docs]

    async def count_notifications(
        self,
        user_id: Optional[int] = None,
        unread_only: bool = False,
    ) -> int:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if unread_only:
            query["read"] = False
        
        return await self.collection.count_documents(query)

    async def mark_as_read(self, notification_id: str) -> bool:
        from bson import ObjectId
        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True}}
        )
        return result.modified_count > 0

    async def mark_all_as_read(self, user_id: int) -> int:
        result = await self.collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
        return result.modified_count