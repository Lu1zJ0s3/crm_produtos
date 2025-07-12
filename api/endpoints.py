import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from django.contrib.auth.hashers import check_password
from crm.models import User as DjangoUser, Product as DjangoProduct, Sale as DjangoSale

from .schemas import (
    SaleBase, Token, TokenData, User, UserCreate,
    Product as ProductSchema, ProductCreate, Sale as SaleSchema
)

# Configurações de segurança
SECRET_KEY: str = os.getenv("SECRET_KEY", "django-insecure-sua-chave-secreta-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str) -> Optional[DjangoUser]:
    try:
        user = DjangoUser.objects.get(username=username)  # type: ignore
        if check_password(password, user.password):
            return user
    except DjangoUser.DoesNotExist:  # type: ignore
        pass
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> DjangoUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = DjangoUser.objects.get(username=username)  # type: ignore
    except (JWTError, DjangoUser.DoesNotExist):  # type: ignore
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: DjangoUser = Depends(get_current_user)):
    return current_user

@app.post("/products", response_model=ProductSchema)
def create_product(product: ProductCreate, current_user: DjangoUser = Depends(get_current_user)):
    if not current_user.is_owner:
        raise HTTPException(status_code=403, detail="Somente donos podem criar produtos.")
    new_product = DjangoProduct.objects.create(**product.dict())  # type: ignore
    return ProductSchema.from_orm(new_product)

@app.get("/products", response_model=list[ProductSchema])
def list_products(current_user: DjangoUser = Depends(get_current_user)):
    products = DjangoProduct.objects.all()  # type: ignore
    return [ProductSchema.from_orm(product) for product in products]

@app.post("/sales", response_model=SaleSchema)
def create_sale(sale: SaleBase, current_user: DjangoUser = Depends(get_current_user)):
    try:
        product = DjangoProduct.objects.get(id=sale.product_id)  # type: ignore
        if product.stock < sale.quantity:
            raise HTTPException(status_code=400, detail="Estoque insuficiente.")
        
        new_sale = DjangoSale.objects.create(  # type: ignore
            product=product,
            quantity=sale.quantity,
            sale_price=sale.price,
            sold_by=current_user
        )
        return SaleSchema.from_orm(new_sale)
    except DjangoProduct.DoesNotExist:  # type: ignore
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
