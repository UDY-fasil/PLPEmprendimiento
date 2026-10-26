"""Main application entry point for PLPE."""
import mimetypes
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Aseguramos los tipos MIME de imágenes (necesario para que el navegador
# las muestre con la cabecera X-Content-Type-Options: nosniff)
for _ext, _type in [
    (".webp", "image/webp"),
    (".svg", "image/svg+xml"),
    (".jpg", "image/jpeg"),
    (".jpeg", "image/jpeg"),
    (".png", "image/png"),
    (".gif", "image/gif"),
]:
    mimetypes.add_type(_type, _ext)

from app.core.config import settings
from app.core.database import init_mongodb, close_mongodb
from app.core.database.mariadb import engine
from app.core.rate_limiter import setup_rate_limiting
from app.core.security_middleware import SecurityHeadersMiddleware

# Import all routers
from app.modules.auth.api import auth_router, user_router, role_router
from app.modules.business.api import (
    business_router,
    category_router,
    product_router,
    service_router,
    favorite_router,
    inquiry_router,
)
from app.modules.audit.api import audit_router
from app.modules.contact.api import contact_router
from app.modules.contact.models import ContactRequest
from app.modules.assistant.api import assistant_router
from app.modules.uploads.api import router as uploads_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize MongoDB (non-blocking - app starts even if unavailable)
    try:
        await init_mongodb()
    except Exception:
        pass  # App starts normally; audit features will be limited if MongoDB is down
    # Ensure contact_requests table exists
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda c: ContactRequest.__table__.create(c, checkfirst=True))
    except Exception:
        pass
    yield
    # Shutdown
    try:
        await close_mongodb()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma para visibilizar y conectar emprendedores y productores locales.",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup rate limiting
setup_rate_limiting(app)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(business_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(service_router)
app.include_router(favorite_router)
app.include_router(inquiry_router)
app.include_router(audit_router)
app.include_router(contact_router)
app.include_router(assistant_router)
app.include_router(uploads_router)


@app.get("/health", tags=["Sistema"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


# ---------------------------------------------------------------------------
# Frontend (archivos estáticos)
# ---------------------------------------------------------------------------
STATIC_DIR = Path(__file__).resolve().parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index():
    """Sirve la aplicación frontend."""
    return FileResponse(STATIC_DIR / "index.html")