from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database.mariadb import Base

class User(Base):
    _tablename_ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="productor") # admin, productor, cliente
    is_active = Column(Boolean, default=True)
    totp_secret = Column(String(255), nullable=True)
    totp_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    businesses = relationship("Business", back_populates="owner")

class Category(Base):
    _tablename_ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

class Business(Base):
    _tablename_ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text)
    city = Column(String(100), index=True)
    is_deleted = Column(Boolean, default=False)  # Soft Delete
    created_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="businesses")
    products = relationship("Product", back_populates="business")

class Product(Base):
    _tablename_ = "products"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(150), nullable=False, index=True)
    price = Column(Integer, nullable=False)
    description = Column(Text)
    is_deleted = Column(Boolean, default=False)  # Soft Delete

    business = relationship("Business", back_populates="products")