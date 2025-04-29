from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import models, schemas, auth
from decimal import Decimal


async def get_user_by_username(db: AsyncSession, username: str):
    q = await db.execute(select(models.User).where(models.User.username == username))
    return q.scalar_one_or_none()


async def create_user(db: AsyncSession, user: schemas.DTO_UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_receipt(db: AsyncSession, user_id: int, rc: schemas.DTO_ReceiptCreate):
    total = Decimal(0)
    db_receipt = models.Receipt(
        owner_id=user_id,
        payment_type=rc.payment.type,
        payment_amount=rc.payment.amount
    )
    db.add(db_receipt)
    await db.flush()
    for p in rc.products:
        line = p.price * p.quantity
        total += line
        item = models.ReceiptItem(
            receipt_id=db_receipt.id,
            name=p.name,
            price=p.price,
            quantity=p.quantity
        )
        db.add(item)
    await db.commit()
    await db.refresh(db_receipt)
    rest = rc.payment.amount - total
    return {
        "id": db_receipt.id,
        "created_at": db_receipt.created_at,
        "products": [
            {"name": p.name, "price": p.price, "quantity": p.quantity, "total": p.price * p.quantity}
            for p in rc.products
        ],
        "payment": rc.payment,
        "total": total,
        "rest": rest
    }


async def get_receipts(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        date_from=None,
        date_to=None,
        min_total=None,
        payment_type=None
):
    stmt = (
        select(models.Receipt)
        .options(selectinload(models.Receipt.items))  # <-- eager-load items
        .where(models.Receipt.owner_id == user_id)
    )
    if date_from:
        stmt = stmt.where(models.Receipt.created_at >= date_from)
    if date_to:
        stmt = stmt.where(models.Receipt.created_at <= date_to)
    if payment_type:
        stmt = stmt.where(models.Receipt.payment_type == payment_type)
    if min_total is not None:
        stmt = (
            stmt.join(models.ReceiptItem)
            .group_by(models.Receipt.id)
            .having(func.sum(models.ReceiptItem.price * models.ReceiptItem.quantity) >= min_total)
        )
    if payment_type:
        stmt = stmt.offset(skip).limit(limit)

    res = await db.execute(stmt)
    return res.scalars().all()


async def get_receipt_by_id(db: AsyncSession, user_id: int, receipt_id: int):
    stmt = (
        select(models.Receipt)
        .options(selectinload(models.Receipt.items))
        .where(
            models.Receipt.owner_id == user_id,
            models.Receipt.id == receipt_id
        )
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()
