"""Activity event repository for MongoDB."""
from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database.mongodb import get_mongo_db
from app.modules.audit.models import ActivityEvent


class ActivityRepository:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_mongo_db()
        return self._db

    @property
    def collection(self):
        return self.db["activity_events"]

    async def create(self, activity: ActivityEvent) -> ActivityEvent:
        doc = activity.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        activity.id = str(result.inserted_id)
        return activity

    async def create_many(self, activities: List[ActivityEvent]) -> List[ActivityEvent]:
        if not activities:
            return []
        docs = [a.model_dump(by_alias=True, exclude={"id"}) for a in activities]
        result = await self.collection.insert_many(docs)
        for i, activity in enumerate(activities):
            activity.id = str(result.inserted_ids[i])
        return activities

    async def list_events(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[ActivityEvent]:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if event_type:
            query["event_type"] = event_type
        if entity:
            query["entity"] = entity
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [ActivityEvent.model_validate(doc) for doc in docs]

    async def count_events(
        self,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if event_type:
            query["event_type"] = event_type
        if entity:
            query["entity"] = entity
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        return await self.collection.count_documents(query)