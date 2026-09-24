from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.database.mariadb import engine, Base, get_db
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db_mongo
from app.models.mariadb import User, Business, Product
from app.schemas.schemas import UserRegister, UserLogin, BusinessCreate, ProductCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de inicio
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await connect_to_mongo()
    yield
    # Evento de cierre
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    lifespan=lifespan
)

# Helper para guardar logs de auditoría en MongoDB
async def log_audit(action: str, user_email: str, details: dict):
    if db_mongo.db is not None:
        await db_mongo.db["audit_logs"].insert_one({
            "action": action,
            "user": user_email,
            "details": details,
            "timestamp": datetime.utcnow()
        })

@app.post("/api/v1/auth/register", status_code=201)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    
    await log_audit("USER_REGISTER", user_data.email, {"role": user_data.role})
    return {"message": "Usuario registrado exitosamente."}

@app.post("/api/v1/auth/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    
    token = create_access_token({"sub": user.email, "role": user.role})
    await log_audit("USER_LOGIN", user.email, {"status": "success"})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/v1/businesses", status_code=201)
async def create_business(data: BusinessCreate, owner_email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == owner_email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado.")
    
    business = Business(
        owner_id=user.id,
        name=data.name,
        description=data.description,
        city=data.city
    )
    db.add(business)
    await db.commit()
    
    await log_audit("BUSINESS_CREATE", owner_email, {"business_name": data.name})
    return {"message": "Emprendimiento creado con éxito.", "business_id": business.id}

@app.get("/api/v1/businesses")
async def list_businesses(page: int = 1, limit: int = 10, db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    result = await db.execute(
        select(Business).where(Business.is_deleted == False).offset(offset).limit(limit)
    )
    businesses = result.scalars().all()
    return {"page": page, "limit": limit, "data": businesses}