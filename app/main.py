from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import timedelta, datetime

from sqlalchemy.orm import selectinload

from app import database, schemas, crud, auth, receipt_formatter, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    yield


app = FastAPI(title="Receipt API", lifespan=lifespan)


@app.post("/register", response_model=schemas.DTO_RegisterResponse, status_code=201)
async def register(
        u: schemas.DTO_UserCreate,
        db: AsyncSession = Depends(database.get_db)
):
    if await crud.get_user_by_username(db, u.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    user = await crud.create_user(db, u)
    return {"message": "User registered", "user": user.username}


@app.post("/login", response_model=schemas.DTO_Token)
async def login(
        response: Response,
        creds: schemas.DTO_LoginIn,
        db: AsyncSession = Depends(database.get_db)
):
    user = await crud.get_user_by_username(db, creds.username)
    if not user or not auth.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="access_token_cookie",
        value=token,
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return {"access_token": token, "token_type": "bearer"}


@app.post("/receipts", response_model=schemas.DTO_ReceiptOut, status_code=201)
async def create_receipt(
        rc: schemas.DTO_ReceiptCreate,
        db: AsyncSession = Depends(database.get_db),
        current_user=Depends(auth.get_current_user)
):
    return await crud.create_receipt(db, current_user.id, rc)


@app.get("/receipts", response_model=List[schemas.DTO_ReceiptOut])
async def list_receipts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1),
        date_from: Optional[datetime] = Query(None),
        date_to: Optional[datetime] = Query(None),
        min_total: Optional[float] = Query(None, ge=0),
        payment_type: Optional[models.PaymentType] = Query(None),
        db: AsyncSession = Depends(database.get_db),
        current_user=Depends(auth.get_current_user)
):
    recs = await crud.get_receipts(
        db, current_user.id, skip, limit, date_from, date_to, min_total, payment_type
    )
    out = []
    for r in recs:
        products = [
            {"name": it.name, "price": it.price, "quantity": it.quantity, "total": it.price * it.quantity}
            for it in r.items
        ]
        total = sum(p["total"] for p in products)
        rest = r.payment_amount - total
        out.append({
            "id": r.id,
            "created_at": r.created_at,
            "products": products,
            "payment": {"type": r.payment_type, "amount": r.payment_amount},
            "total": total,
            "rest": rest
        })
    return out


@app.get("/receipts/{receipt_id}", response_model=schemas.DTO_ReceiptOut)
async def get_receipt(
        receipt_id: int,
        db: AsyncSession = Depends(database.get_db),
        current_user=Depends(auth.get_current_user)
):
    r = await crud.get_receipt_by_id(db, current_user.id, receipt_id)
    if not r:
        raise HTTPException(404, "Receipt not found")
    return {
        "id": r.id,
        "created_at": r.created_at,
        "products": [
            {"name": it.name, "price": it.price, "quantity": it.quantity, "total": it.price * it.quantity}
            for it in r.items
        ],
        "payment": {"type": r.payment_type, "amount": r.payment_amount},
        "total": sum(it.price * it.quantity for it in r.items),
        "rest": r.payment_amount - sum(it.price * it.quantity for it in r.items)
    }


@app.get("/public/receipts/{receipt_id}", response_class=PlainTextResponse)
async def public_receipt(
    receipt_id: int,
    width: int = Query(40, ge=20),
    db: AsyncSession = Depends(database.get_db)
):
    stmt = (
        select(models.Receipt)
        .options(selectinload(models.Receipt.items))
        .where(models.Receipt.id == receipt_id)
    )
    res = await db.execute(stmt)
    r = res.scalar_one_or_none()

    if not r:
        raise HTTPException(404, "Receipt not found")

    data = {
        "id": r.id,
        "created_at": r.created_at,
        "products": [
            {
                "name": it.name,
                "price": it.price,
                "quantity": it.quantity,
                "total": it.price * it.quantity
            }
            for it in r.items
        ],
        "payment": {"type": r.payment_type, "amount": r.payment_amount},
        "total": sum(it.price * it.quantity for it in r.items),
        "rest": r.payment_amount - sum(it.price * it.quantity for it in r.items)
    }
    text = receipt_formatter.format_receipt(data, width)
    return text


def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
