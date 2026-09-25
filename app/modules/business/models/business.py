"""Business model for business module."""
from datetime import datetime
from sqlalchemy import (
    String, Integer, Text, ForeignKey, Enum, Index, func, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.mariadb import Base
import enum


class BusinessStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        Index("ix_businesses_city", "city"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100), index=True)
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[BusinessStatus] = mapped_column(
        Enum(BusinessStatus), default=BusinessStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    owner: Mapped["User"] = relationship(back_populates="businesses")
    categories: Mapped[list["Category"]] = relationship(
        secondary="business_categories", back_populates="businesses"
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    services: Mapped[list["Service"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    inquiries: Mapped[list["Inquiry"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )