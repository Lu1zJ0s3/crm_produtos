from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_owner: bool

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProductCreate(ProductBase):
    price: float
    stock: int

class Product(ProductBase):
    id: int
    price: float
    stock: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    product_id: int
    quantity: int
    price: float  

class Sale(SaleBase):
    id: int
    created_at: datetime
    sold_by: User

    class Config:
        from_attributes = True
