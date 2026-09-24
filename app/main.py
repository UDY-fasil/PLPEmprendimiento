from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.mongodb import init_mongodb, close_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # MariaDB: las tablas las maneja Alembic (NO create_all)
    await init_mongodb()
    yield
    # Shutdown
    await close_mongodb()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}