"""Business API request/response schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class BusinessCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    category_ids: List[int] = Field(default_factory=list)


class BusinessUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    category_ids: Optional[List[int]] = None


class BusinessResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    address: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    status: str
    categories: List["CategoryResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessListResponse(BaseModel):
    businesses: List[BusinessResponse]
    total: int
    page: int
    page_size: int


class CategoryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int
    page: int
    page_size: int


class ProductCreateRequest(BaseModel):
    business_id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "ARS"
    stock: Optional[int] = None
    image_url: Optional[str] = None


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    business_id: int
    name: str
    description: Optional[str]
    price: Optional[float]
    currency: str
    stock: Optional[int]
    image_url: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


class ServiceCreateRequest(BaseModel):
    business_id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "ARS"
    duration_minutes: Optional[int] = None
    image_url: Optional[str] = None


class ServiceUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None


class ServiceResponse(BaseModel):
    id: int
    business_id: int
    name: str
    description: Optional[str]
    price: Optional[float]
    currency: str
    duration_minutes: Optional[int]
    image_url: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceListResponse(BaseModel):
    services: List[ServiceResponse]
    total: int
    page: int
    page_size: int


class FavoriteCreateRequest(BaseModel):
    business_id: Optional[int] = None
    product_id: Optional[int] = None


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    business_id: Optional[int]
    product_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteResponse]
    total: int
    page: int
    page_size: int


class InquiryCreateRequest(BaseModel):
    business_id: int
    sender_name: str
    sender_email: EmailStr
    sender_phone: Optional[str] = None
    message: str


class InquiryResponse(BaseModel):
    id: int
    business_id: int
    sender_id: Optional[int]
    sender_name: str
    sender_email: str
    sender_phone: Optional[str]
    message: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime]

    model_config = {"from_attributes": True}


class InquiryListResponse(BaseModel):
    inquiries: List[InquiryResponse]
    total: int
    page: int
    page_size: int


class InquiryStatusUpdate(BaseModel):
    status: str


BusinessResponse.model_rebuild()
CategoryResponse.model_rebuild()
ProductResponse.model_rebuild()
ServiceResponse.model_rebuild()
FavoriteResponse.model_rebuild()