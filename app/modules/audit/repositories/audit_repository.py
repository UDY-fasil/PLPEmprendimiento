"""Audit log repository for MongoDB."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database.mongodb import get_mongo_db
from app.modules.audit.models import AuditLog


class AuditRepository:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_mongo_db()
        return self._db

    @property
    def collection(self):
        return self.db["audit_logs"]

    async def create(self, audit_log: AuditLog) -> AuditLog:
        doc = audit_log.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        audit_log.id = str(result.inserted_id)
        return audit_log

    async def get_by_id(self, audit_id: str) -> Optional[AuditLog]:
        from bson import ObjectId
        doc = await self.collection.find_one({"_id": ObjectId(audit_id)})
        if doc:
            return AuditLog.model_validate(doc)
        return None

    async def list_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditLog]:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
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
        return [AuditLog.model_validate(doc) for doc in docs]

    async def count_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = {}
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        if entity:
            query["entity"] = entity
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        return await self.collection.count_documents(query)