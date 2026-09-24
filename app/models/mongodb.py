from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_mongo = MongoDB()

async def connect_to_mongo():
    db_mongo.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_mongo.db = db_mongo.client["plpe_audit"]
    # Crear TTL index para cached_searches (24 horas = 86400s)
    await db_mongo.db["cached_searches"].create_index("createdAt", expireAfterSeconds=86400)

async def close_mongo_connection():
    db_mongo.client.close()