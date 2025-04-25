from pydantic import BaseModel, condecimal
from typing import List, Optional
from datetime import datetime
from .models import PaymentType

class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str

class RegisterResponse(BaseModel):
    message: str
    user: str

class LoginIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class ProductIn(BaseModel):
    name: str
    price: condecimal(max_digits=12, decimal_places=2)
    quantity: condecimal(max_digits=12, decimal_places=3)

class PaymentIn(BaseModel):
    type: PaymentType
    amount: condecimal(max_digits=12, decimal_places=2)

class ReceiptCreate(BaseModel):
    products: List[ProductIn]
    payment: PaymentIn

class ProductOut(ProductIn):
    total: condecimal(max_digits=14, decimal_places=2)

class ReceiptOut(BaseModel):
    id: int
    created_at: datetime
    products: List[ProductOut]
    payment: PaymentIn
    total: condecimal(max_digits=14, decimal_places=2)
    rest: condecimal(max_digits=14, decimal_places=2)

    model_config = {
        "from_attributes": True
    }
