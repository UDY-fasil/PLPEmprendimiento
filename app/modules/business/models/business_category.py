"""BusinessCategory association model for business module."""
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database.mariadb import Base


class BusinessCategory(Base):
    __tablename__ = "business_categories"
    __table_args__ = (
        UniqueConstraint("business_id", "category_id", name="uq_business_category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))