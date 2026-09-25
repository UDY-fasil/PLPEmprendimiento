"""Cached search repository for MongoDB."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database.mongodb import get_mongo_db
from app.modules.audit.models import CachedSearch


class CachedSearchRepository:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_mongo_db()
        return self._db

    @property
    def collection(self):
        return self.db["cached_searches"]

    async def create(self, cached_search: CachedSearch) -> CachedSearch:
        doc = cached_search.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        cached_search.id = str(result.inserted_id)
        return cached_search

    async def get_by_query_hash(self, query_hash: str) -> Optional[CachedSearch]:
        doc = await self.collection.find_one({"query_hash": query_hash})
        if doc:
            return CachedSearch.model_validate(doc)
        return None

    async def get_valid_by_query_hash(self, query_hash: str) -> Optional[CachedSearch]:
        doc = await self.collection.find_one({
            "query_hash": query_hash,
            "created_at": {"$gte": datetime.utcnow()},
        })
        if doc:
            return CachedSearch.model_validate(doc)
        return None

    async def update_results(self, query_hash: str, results: List[Dict[str, Any]]) -> bool:
        result = await self.collection.update_one(
            {"query_hash": query_hash},
            {"$set": {"results": results, "created_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def delete_expired(self) -> int:
        result = await self.collection.delete_many({
            "created_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count