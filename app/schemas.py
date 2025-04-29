from pydantic import BaseModel, condecimal
from typing import List, Optional
from datetime import datetime
from .models import PaymentType

class DTO_UserCreate(BaseModel):
    username: str
    full_name: str
    password: str

class DTO_RegisterResponse(BaseModel):
    message: str
    user: str

class DTO_LoginIn(BaseModel):
    username: str
    password: str

class DTO_Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DTO_TokenData(BaseModel):
    username: Optional[str] = None

class DTO_ProductIn(BaseModel):
    name: str
    price: condecimal(max_digits=12, decimal_places=2)
    quantity: condecimal(max_digits=12, decimal_places=3)

class DTO_PaymentIn(BaseModel):
    type: PaymentType
    amount: condecimal(max_digits=12, decimal_places=2)

class DTO_ReceiptCreate(BaseModel):
    products: List[DTO_ProductIn]
    payment: DTO_PaymentIn

class DTO_ProductOut(DTO_ProductIn):
    total: condecimal(max_digits=14, decimal_places=2)

class DTO_ReceiptOut(BaseModel):
    id: int
    created_at: datetime
    products: List[DTO_ProductOut]
    payment: DTO_PaymentIn
    total: condecimal(max_digits=14, decimal_places=2)
    rest: condecimal(max_digits=14, decimal_places=2)

    model_config = {
        "from_attributes": True
    }
