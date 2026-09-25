"""Favorite model for business module."""
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.mariadb import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "business_id", "product_id", name="uq_favorite"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    business_id: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE")
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="favorites")
    business: Mapped["Business | None"] = relationship(back_populates="favorites")
    product: Mapped["Product | None"] = relationship(back_populates="favorites")