"""Rate limiting and security configuration."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """Get client IP address, considering proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.LOGIN_MAX_ATTEMPTS}/minute"] if settings.APP_ENV == "production" else [],
    storage_uri="memory://",
)


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_limiter() -> Limiter:
    return limiter