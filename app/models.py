from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class PaymentType(str, enum.Enum):
    cash = "cash"
    cashless = "cashless"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    receipts = relationship("Receipt", back_populates="owner")

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_amount = Column(Numeric(12,2), nullable=False)
    owner = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")

class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    name = Column(String, nullable=False)
    price = Column(Numeric(12,2), nullable=False)
    quantity = Column(Numeric(12,3), nullable=False)
    receipt = relationship("Receipt", back_populates="items")
