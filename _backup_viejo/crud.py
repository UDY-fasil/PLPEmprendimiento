import math
from sqlalchemy.orm import Session
from . import models, schemas

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia entre dos puntos geográficos utilizando la fórmula de Haversine."""
    R = 6371  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def crear_productor(db: Session, productor: schemas.ProductorCreate):
    db_productor = models.Productor(**productor.model_dump())
    db.add(db_productor)
    db.commit()
    db.refresh(db_productor)
    return db_productor

def buscar_productores_cercanos(db: Session, lat_usuario: float, lon_usuario: float, radio_km: float = 10.0):
    todos = db.query(models.Productor).filter(models.Productor.es_activo == True).all()
    cercanos = []
    for prod in todos:
        distancia = haversine(lat_usuario, lon_usuario, prod.latitud, prod.longitud)
        if distancia <= radio_km:
            cercanos.append(prod)
    return cercanos

def crear_producto(db: Session, producto: schemas.ProductoCreate, productor_id: int):
    db_producto = models.Producto(**producto.model_dump(), productor_id=productor_id)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto