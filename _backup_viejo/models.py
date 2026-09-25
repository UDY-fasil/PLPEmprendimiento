from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    # 'Column' debe ir con C mayúscula
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    descripcion = Column(String)

    # 'Producto' debe ir con P mayúscula
    productos = relationship("Producto", back_populates="categoria")

class Productor(Base):
    __tablename__ = "productores"

    id = Column(Integer, primary_key=True, index=True)
    nombre_comercial = Column(String, index=True)
    descripcion = Column(Text)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    direccion = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    es_activo = Column(Boolean, default=True)

    productos = relationship("Producto", back_populates="productor")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(Text)
    precio = Column(Float, nullable=True)
    unidad_medida = Column(String)
    disponible = Column(Boolean, default=True)
    
    productor_id = Column(Integer, ForeignKey("productores.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    productor = relationship("Productor", back_populates="productos")
    categoria = relationship("Categoria", back_populates="productos")