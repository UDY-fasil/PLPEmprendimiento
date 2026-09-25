"""Shared helpers for PLPE scripts."""
import os
import socket
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.config import settings  # noqa: E402


def resolve_db_url() -> str:
    """Return a usable MariaDB URL.

    - `PLPE_DB_URL` environment variable has highest priority.
    - If running inside Docker, the host `mariadb` resolves.
    - Otherwise fall back to `localhost` so scripts can run from the host.
    """
    override = os.getenv("PLPE_DB_URL")
    if override:
        return override

    url = settings.MARIADB_URL
    try:
        socket.gethostbyname("mariadb")
        return url
    except socket.gaierror:
        return url.replace("@mariadb:", "@localhost:")
