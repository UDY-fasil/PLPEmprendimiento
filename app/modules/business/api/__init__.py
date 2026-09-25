"""Business API routers with real implementations."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.modules.auth.dependencies import get_current_user, get_current_active_user, get_current_user_optional
from app.modules.auth.models import User
from app.modules.business.dependencies import (
    get_business_service,
    get_category_service,
    get_product_service,
    get_service_service,
    get_favorite_service,
    get_inquiry_service,
    require_business_owner,
    require_business_owner_or_admin,
)
from app.modules.business.services import (
    BusinessService,
    CategoryService,
    ProductService,
    ServiceService,
    FavoriteService,
    InquiryService,
)
from app.modules.business.models import Business, BusinessStatus, InquiryStatus
from app.modules.business.schemas.api import (
    BusinessCreateRequest,
    BusinessUpdateRequest,
    BusinessResponse,
    BusinessListResponse,
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceResponse,
    ServiceListResponse,
    FavoriteCreateRequest,
    FavoriteResponse,
    FavoriteListResponse,
    InquiryCreateRequest,
    InquiryResponse,
    InquiryListResponse,
    InquiryStatusUpdate,
)


def _is_admin(user: User) -> bool:
    """Indica si el usuario tiene el rol admin."""
    return "admin" in {role.name for role in user.roles}


# Business router
business_router = APIRouter(prefix="/businesses", tags=["Negocios"])


@business_router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    data: BusinessCreateRequest,
    current_user: User = Depends(get_current_active_user),
    business_service: BusinessService = Depends(get_business_service),
):
    """Crear un nuevo emprendimiento."""
    try:
        business = await business_service.create_business(
            owner_id=current_user.id,
            data=data,
        )
        return BusinessResponse.model_validate(business)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@business_router.get("", response_model=BusinessListResponse)
async def list_businesses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[BusinessStatus] = None,
    city: Optional[str] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    business_service: BusinessService = Depends(get_business_service),
):
    """Listar emprendimientos con filtros y paginación."""
    businesses, total = await business_service.list_businesses(
        page=page,
        page_size=page_size,
        status=status,
        city=city,
        category_id=category_id,
        search=search,
    )
    return BusinessListResponse(
        businesses=[BusinessResponse.model_validate(b) for b in businesses],
        total=total,
        page=page,
        page_size=page_size,
    )


@business_router.get("/my", response_model=BusinessListResponse)
async def list_my_businesses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[BusinessStatus] = None,
    current_user: User = Depends(get_current_active_user),
    business_service: BusinessService = Depends(get_business_service),
):
    """Listar mis emprendimientos (mi entorno de trabajo)."""
    businesses, total = await business_service.list_businesses(
        page=page,
        page_size=page_size,
        owner_id=current_user.id,
        search=search,
        status=status,
    )
    return BusinessListResponse(
        businesses=[BusinessResponse.model_validate(b) for b in businesses],
        total=total,
        page=page,
        page_size=page_size,
    )


@business_router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: int,
    business_service: BusinessService = Depends(get_business_service),
):
    """Obtener un emprendimiento por ID."""
    business = await business_service.get_business(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return BusinessResponse.model_validate(business)


@business_router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    data: BusinessUpdateRequest,
    business: Business = Depends(require_business_owner),
    business_service: BusinessService = Depends(get_business_service),
):
    """Actualizar un emprendimiento (solo propietario)."""
    updated = await business_service.update_business(
        business_id=business_id,
        owner_id=business.owner_id,
        data=data,
    )
    return BusinessResponse.model_validate(updated)


@business_router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: int,
    business: Business = Depends(require_business_owner),
    business_service: BusinessService = Depends(get_business_service),
):
    """Eliminar un emprendimiento (soft delete, solo propietario)."""
    success = await business_service.delete_business(business_id, business.owner_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")


# Admin endpoints for business moderation
@business_router.post("/{business_id}/approve", response_model=BusinessResponse)
async def approve_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    business_service: BusinessService = Depends(get_business_service),
):
    """Aprobar un emprendimiento (solo admin)."""
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    
    business = await business_service.approve_business(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return BusinessResponse.model_validate(business)


@business_router.post("/{business_id}/suspend", response_model=BusinessResponse)
async def suspend_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    business_service: BusinessService = Depends(get_business_service),
):
    """Suspender un emprendimiento (solo admin)."""
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    
    business = await business_service.suspend_business(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return BusinessResponse.model_validate(business)


# Category router
category_router = APIRouter(prefix="/categories", tags=["Categorías"])


@category_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """Crear categoría (solo admin)."""
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

    try:
        category = await category_service.create_category(data)
        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@category_router.get("", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    active_only: bool = True,
    category_service: CategoryService = Depends(get_category_service),
):
    """Listar categorías."""
    categories, total = await category_service.list_categories(
        page=page,
        page_size=page_size,
        active_only=active_only,
    )
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
    )


@category_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    """Obtener categoría por ID."""
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryResponse.model_validate(category)


@category_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """Actualizar categoría (solo admin)."""
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")

    try:
        category = await category_service.update_category(
            category_id=category_id,
            name=data.name,
            description=data.description,
            icon=data.icon,
            active=data.active,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryResponse.model_validate(category)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """Eliminar categoría (solo admin)."""
    user_roles = {role.name for role in current_user.roles}
    if "admin" not in user_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    
    success = await category_service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


# Product router
product_router = APIRouter(prefix="/products", tags=["Productos"])


@product_router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreateRequest,
    current_user: User = Depends(get_current_active_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Crear producto."""
    try:
        product = await product_service.create_product(
            business_id=data.business_id,
            owner_id=current_user.id,
            data=data,
            is_admin=_is_admin(current_user),
        )
        return ProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@product_router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    business_id: Optional[int] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    product_service: ProductService = Depends(get_product_service),
):
    """Listar productos."""
    products, total = await product_service.list_products(
        page=page,
        page_size=page_size,
        business_id=business_id,
        active_only=active_only,
        search=search,
    )
    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@product_router.get("/my", response_model=ProductListResponse)
async def list_my_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Listar los productos del usuario actual (su entorno de trabajo)."""
    products, total = await product_service.list_products(
        page=page,
        page_size=page_size,
        active_only=active_only,
        search=search,
        owner_id=current_user.id,
    )
    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@product_router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """Obtener producto por ID."""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@product_router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Actualizar producto (propietario del negocio o admin)."""
    product = await product_service.get_product_with_business(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not _is_admin(current_user) and product.business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        updated = await product_service.update_product(
            product_id=product_id,
            owner_id=current_user.id,
            data=data,
            is_admin=_is_admin(current_user),
        )
        return ProductResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    product_service: ProductService = Depends(get_product_service),
):
    """Eliminar producto (propietario del negocio o admin)."""
    product = await product_service.get_product_with_business(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not _is_admin(current_user) and product.business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        success = await product_service.delete_product(
            product_id, current_user.id, is_admin=_is_admin(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


# Service router
service_router = APIRouter(prefix="/services", tags=["Servicios"])


@service_router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreateRequest,
    current_user: User = Depends(get_current_active_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Crear servicio."""
    try:
        service = await service_service.create_service(
            business_id=data.business_id,
            owner_id=current_user.id,
            data=data,
            is_admin=_is_admin(current_user),
        )
        return ServiceResponse.model_validate(service)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@service_router.get("", response_model=ServiceListResponse)
async def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    business_id: Optional[int] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    service_service: ServiceService = Depends(get_service_service),
):
    """Listar servicios."""
    services, total = await service_service.list_services(
        page=page,
        page_size=page_size,
        business_id=business_id,
        active_only=active_only,
        search=search,
    )
    return ServiceListResponse(
        services=[ServiceResponse.model_validate(s) for s in services],
        total=total,
        page=page,
        page_size=page_size,
    )


@service_router.get("/my", response_model=ServiceListResponse)
async def list_my_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Listar los servicios del usuario actual (su entorno de trabajo)."""
    services, total = await service_service.list_services(
        page=page,
        page_size=page_size,
        active_only=active_only,
        search=search,
        owner_id=current_user.id,
    )
    return ServiceListResponse(
        services=[ServiceResponse.model_validate(s) for s in services],
        total=total,
        page=page,
        page_size=page_size,
    )


@service_router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    service_service: ServiceService = Depends(get_service_service),
):
    """Obtener servicio por ID."""
    service = await service_service.get_service(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return ServiceResponse.model_validate(service)


@service_router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    data: ServiceUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Actualizar servicio (propietario del negocio o admin)."""
    service = await service_service.get_service_with_business(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    if not _is_admin(current_user) and service.business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        updated = await service_service.update_service(
            service_id=service_id,
            owner_id=current_user.id,
            data=data,
            is_admin=_is_admin(current_user),
        )
        return ServiceResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@service_router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_active_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Eliminar servicio (propietario del negocio o admin)."""
    service = await service_service.get_service_with_business(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    if not _is_admin(current_user) and service.business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        success = await service_service.delete_service(
            service_id, current_user.id, is_admin=_is_admin(current_user)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")


# Favorite router
favorite_router = APIRouter(prefix="/favorites", tags=["Favoritos"])


@favorite_router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    data: FavoriteCreateRequest,
    current_user: User = Depends(get_current_active_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Agregar a favoritos."""
    try:
        favorite = await favorite_service.add_favorite(
            user_id=current_user.id,
            data=data,
        )
        return FavoriteResponse.model_validate(favorite)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@favorite_router.get("", response_model=FavoriteListResponse)
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Listar favoritos del usuario actual."""
    favorites, total = await favorite_service.list_favorites(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return FavoriteListResponse(
        favorites=[FavoriteResponse.model_validate(f) for f in favorites],
        total=total,
        page=page,
        page_size=page_size,
    )


@favorite_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    business_id: Optional[int] = None,
    product_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Quitar de favoritos."""
    if not business_id and not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="business_id or product_id required")
    
    success = await favorite_service.remove_favorite(
        user_id=current_user.id,
        business_id=business_id,
        product_id=product_id,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")


@favorite_router.get("/check", response_model=dict)
async def check_favorite(
    business_id: Optional[int] = None,
    product_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Verificar si está en favoritos."""
    if not business_id and not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="business_id or product_id required")
    
    is_fav = await favorite_service.is_favorite(
        user_id=current_user.id,
        business_id=business_id,
        product_id=product_id,
    )
    return {"is_favorite": is_fav}


# Inquiry router
inquiry_router = APIRouter(prefix="/inquiries", tags=["Consultas"])


@inquiry_router.post("", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    data: InquiryCreateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Crear consulta a un emprendimiento."""
    sender_id = current_user.id if current_user else None
    try:
        inquiry = await inquiry_service.create_inquiry(
            sender_id=sender_id,
            data=data,
        )
        return InquiryResponse.model_validate(inquiry)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@inquiry_router.get("", response_model=InquiryListResponse)
async def list_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    business_id: Optional[int] = None,
    status: Optional[InquiryStatus] = None,
    current_user: User = Depends(get_current_active_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Listar consultas (admin ve todas, usuarios ven las suyas)."""
    user_roles = {role.name for role in current_user.roles}
    sender_id = None if "admin" in user_roles else current_user.id
    
    inquiries, total = await inquiry_service.list_inquiries(
        page=page,
        page_size=page_size,
        business_id=business_id,
        sender_id=sender_id,
        status=status,
    )
    return InquiryListResponse(
        inquiries=[InquiryResponse.model_validate(i) for i in inquiries],
        total=total,
        page=page,
        page_size=page_size,
    )


@inquiry_router.get("/my", response_model=InquiryListResponse)
async def list_my_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Listar mis consultas enviadas."""
    inquiries, total = await inquiry_service.get_my_inquiries(
        sender_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return InquiryListResponse(
        inquiries=[InquiryResponse.model_validate(i) for i in inquiries],
        total=total,
        page=page,
        page_size=page_size,
    )


@inquiry_router.get("/received", response_model=InquiryListResponse)
async def list_received_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[InquiryStatus] = None,
    current_user: User = Depends(get_current_active_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Listar las consultas recibidas en los emprendimientos del usuario actual."""
    inquiries, total = await inquiry_service.list_inquiries(
        page=page,
        page_size=page_size,
        status=status,
        owner_id=current_user.id,
    )
    return InquiryListResponse(
        inquiries=[InquiryResponse.model_validate(i) for i in inquiries],
        total=total,
        page=page,
        page_size=page_size,
    )


@inquiry_router.get("/business/{business_id}", response_model=InquiryListResponse)
async def list_business_inquiries(
    business_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Listar consultas de un emprendimiento (solo propietario)."""
    inquiries, total = await inquiry_service.get_business_inquiries(
        business_id=business_id,
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return InquiryListResponse(
        inquiries=[InquiryResponse.model_validate(i) for i in inquiries],
        total=total,
        page=page,
        page_size=page_size,
    )


@inquiry_router.patch("/{inquiry_id}/status", response_model=InquiryResponse)
async def update_inquiry_status(
    inquiry_id: int,
    data: InquiryStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    inquiry_service: InquiryService = Depends(get_inquiry_service),
):
    """Actualizar estado de consulta (solo propietario del negocio)."""
    try:
        status_enum = InquiryStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    
    inquiry = await inquiry_service.update_inquiry_status(
        inquiry_id=inquiry_id,
        status=status_enum,
        owner_id=current_user.id,
    )
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found")
    return InquiryResponse.model_validate(inquiry)