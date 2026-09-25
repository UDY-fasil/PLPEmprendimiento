from pydantic import BaseModel
from typing import Optional, List

#esquemas de producto
class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    precio: Optional[float] = None
    unidad_medida: Optional[List[str]] = None
    disponible: Optional[bool] = True
    categoria_id: int
    
class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    productor_id: int

    class Config:
        from_attributes = True
#esquema de productor
class ProductorBase(BaseModel):
    nombre_comercial: str
    descripcion: Optional[str] = None
    email: str
    telefono: str
    direccion: str
    latitud: float
    longitud: float

class ProductorCreate(ProductorBase):
    pass

class ProductorResponse(ProductorBase):
    id: int
    es_activo: bool
    productos: List[ProductoResponse] = []
    class Config:
        from_attributes = True