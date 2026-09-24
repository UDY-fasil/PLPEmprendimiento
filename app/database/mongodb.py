from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)   # ← CAMBIO
    return _client


def get_mongo_db() -> AsyncIOMotorDatabase:
    return get_mongo_client()["plpe_audit"]                   # ← CAMBIO (nombre directo)


async def init_mongodb() -> None:
    """Crea colecciones e índices requeridos en MongoDB."""
    db = get_mongo_db()

    # audit_logs
    if "audit_logs" not in await db.list_collection_names():
        await db.create_collection("audit_logs")
    await db["audit_logs"].create_index("created_at")
    await db["audit_logs"].create_index("user_id")
    await db["audit_logs"].create_index("action")

    # activity_events con TTL 180 días
    if "activity_events" not in await db.list_collection_names():
        await db.create_collection("activity_events")
    await db["activity_events"].create_index(
        "created_at", expireAfterSeconds=180 * 24 * 3600
    )
    await db["activity_events"].create_index("event_type")

    # notifications_history
    if "notifications_history" not in await db.list_collection_names():
        await db.create_collection("notifications_history")
    await db["notifications_history"].create_index("user_id")

    # cached_searches con TTL 24 horas
    if "cached_searches" not in await db.list_collection_names():
        await db.create_collection("cached_searches")
    await db["cached_searches"].create_index(
        "created_at", expireAfterSeconds=24 * 3600
    )
    await db["cached_searches"].create_index("query_hash", unique=True)


async def close_mongodb() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None