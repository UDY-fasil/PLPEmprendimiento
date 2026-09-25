"""Inquiry model for business module."""
from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.mariadb import Base
import enum


class InquiryStatus(str, enum.Enum):
    NEW = "new"
    READ = "read"
    ANSWERED = "answered"
    CLOSED = "closed"


class Inquiry(Base):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    sender_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    sender_name: Mapped[str] = mapped_column(String(150), nullable=False)
    sender_email: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_phone: Mapped[str | None] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InquiryStatus] = mapped_column(
        Enum(InquiryStatus), default=InquiryStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime)

    business: Mapped["Business"] = relationship(back_populates="inquiries")