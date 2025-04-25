from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas, auth
from decimal import Decimal
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, full_name=user.full_name, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_receipt(db: Session, user_id: int, receipt_in: schemas.ReceiptCreate):
    total = Decimal(0)
    db_receipt = models.Receipt(owner_id=user_id,
                                payment_type=receipt_in.payment.type,
                                payment_amount=receipt_in.payment.amount)
    db.add(db_receipt)
    for p in receipt_in.products:
        line_total = p.price * p.quantity
        total += line_total
        item = models.ReceiptItem(receipt=db_receipt,
                                  name=p.name,
                                  price=p.price,
                                  quantity=p.quantity)
        db.add(item)
    db.commit()
    db.refresh(db_receipt)
    rest = receipt_in.payment.amount - total
    return {
        "id": db_receipt.id,
        "created_at": db_receipt.created_at,
        "products": [{"name": p.name, "price": p.price, "quantity": p.quantity, "total": p.price * p.quantity}
                     for p in receipt_in.products],
        "payment": receipt_in.payment,
        "total": total,
        "rest": rest
    }

def get_receipts(db: Session, user_id: int, skip: int = 0, limit: int = 10,
                 date_from: datetime = None, date_to: datetime = None,
                 min_total: Decimal = None, payment_type: str = None):
    q = db.query(models.Receipt).filter(models.Receipt.owner_id == user_id)
    if date_from:
        q = q.filter(models.Receipt.created_at >= date_from)
    if date_to:
        q = q.filter(models.Receipt.created_at <= date_to)
    if min_total:
        q = (
            q.join(models.ReceiptItem)
            .group_by(models.Receipt.id)
            .having(func.sum(models.ReceiptItem.price * models.ReceiptItem.quantity) >= min_total)
        )
    if payment_type:
        q = q.filter(models.Receipt.payment_type == payment_type)
    return q.offset(skip).limit(limit).all()

def get_receipt_by_id(db: Session, user_id: int, receipt_id: int):
    return db.query(models.Receipt).filter(models.Receipt.owner_id == user_id,
                                           models.Receipt.id == receipt_id).first()
