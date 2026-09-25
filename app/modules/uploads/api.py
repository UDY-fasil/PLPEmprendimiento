"""Subida de imágenes (para iconos, etc.)."""
import base64
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/uploads", tags=["Subidas"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}
MAX_BYTES = 3 * 1024 * 1024  # 3 MB


class ImageUploadRequest(BaseModel):
    data: str  # Data URL (data:image/png;base64,...) o base64 puro


@router.post("/image")
async def upload_image(payload: ImageUploadRequest):
    """Guarda una imagen y devuelve su URL pública."""
    data = (payload.data or "").strip()
    match = re.match(r"^data:(image/[a-zA-Z0-9.+-]+);base64,(.+)$", data, re.DOTALL)
    if match:
        mime = match.group(1).lower()
        b64 = match.group(2)
    else:
        mime = "image/png"
        b64 = data

    if mime not in ALLOWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado. Usá PNG, JPG, GIF o WEBP.",
        )

    try:
        raw = base64.b64decode(b64, validate=True)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen inválida.")

    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen es demasiado grande (máximo 3 MB).",
        )

    filename = f"{uuid.uuid4().hex}.{ALLOWED[mime]}"
    (UPLOAD_DIR / filename).write_bytes(raw)
    return {"url": f"/static/uploads/{filename}"}
