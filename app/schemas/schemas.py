from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "productor"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None

class BusinessCreate(BaseModel):
    name: str
    description: str
    city: str

class ProductCreate(BaseModel):
    business_id: int
    name: str
    price: int
    description: str