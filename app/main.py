from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud
from .database import engine, get_db

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.mongodb import init_mongodb, close_mongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # MariaDB: las tablas las maneja Alembic (NO create_all)
    await init_mongodb()
    yield
    # Shutdown
    await close_mongodb()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#crea las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)   

app = FastAPI(title="API oferta productiva local - Formosa Hack", description="Plataforma para visivilizar y conectar emprendedores y productores locales.", version="1.0.0")

#Endpoints: Registrar un nuevo productor
@app.post("/productores/", response_model=schemas.ProductorResponse, tags=["Productores"])
def registrar_productor(productor: schemas.ProductorCreate, db: Session = Depends(get_db)):
    db_productor = crud.crear_productor(db=db, productor=productor)
    return db_productor

#Endpoints: Buscar productores por geocalización (mapa / cercanía)
@app.get("/productores/cercanos/", response_model=List[schemas.ProductorResponse], tags=["Consumidores"])
def obtener_productores_cercanos(lat: float, lon: float, radio: float = 10.0, db: Session = Depends(get_db)):
    productores_cercanos = crud.buscar_productores_cercanos(db=db, lat_usuario=lat, lon_usuario=lon, radio_km=radio)
    return productores_cercanos

#Endpoints: cargar oferta de producto
@app.post("/productores/{productor_id}/productos/", response_model=schemas.ProductoResponse, tags=["Productos"])
def cargar_producto(productor_id: int, producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = crud.crear_producto(db=db, producto=producto, productor_id=productor_id)
    return db_producto


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}