"""Contact request model (solicitudes para ser contactado por la administración)."""
import enum
from datetime import datetime

from sqlalchemy import String, Integer, Text, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.mariadb import Base


class ContactRequestStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    CLOSED = "closed"


class ContactRequest(Base):
    __tablename__ = "contact_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ContactRequestStatus] = mapped_column(
        Enum(ContactRequestStatus), default=ContactRequestStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    handled_at: Mapped[datetime | None] = mapped_column(DateTime)
