import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app import database, schemas, crud, auth, receipt_formatter, models

app = FastAPI(title="Receipt API")

database.Base.metadata.create_all(bind=database.engine)


@app.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    u: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    if crud.get_user_by_username(db, u.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    user = crud.create_user(db, u)
    return {
        "message": "User registered",
        "user": user.username
    }


@app.post(
    "/login",
    response_model=schemas.Token
)
def login(
    response: Response,
    creds: schemas.LoginIn,
    db: Session = Depends(database.get_db)
):
    user = crud.get_user_by_username(db, creds.username)
    if not user or not auth.verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post(
    "/receipts",
    response_model=schemas.ReceiptOut,
    status_code=status.HTTP_201_CREATED
)
def create_receipt(
    rc: schemas.ReceiptCreate,
    db: Session = Depends(database.get_db),
    current_user=Depends(auth.get_current_user)
):
    result = crud.create_receipt(db, current_user.id, rc)
    return result


@app.get(
    "/receipts",
    response_model=List[schemas.ReceiptOut]
)
def list_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    min_total: Optional[float] = Query(None, ge=0),
    payment_type: Optional[models.PaymentType] = Query(
        None,
        description="Тип оплати: cash або cashless"
    ),
    db: Session = Depends(database.get_db),
    current_user=Depends(auth.get_current_user),
):
    recs = crud.get_receipts(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        min_total=min_total,
        payment_type=payment_type,
    )
    response_list = []
    for r in recs:
        products = [
            {"name": it.name, "price": it.price, "quantity": it.quantity, "total": it.price * it.quantity}
            for it in r.items
        ]
        total_amount = sum(item["total"] for item in products)
        rest_amount = r.payment_amount - total_amount
        response_list.append({
            "id": r.id,
            "created_at": r.created_at,
            "products": products,
            "payment": {"type": r.payment_type, "amount": r.payment_amount},
            "total": total_amount,
            "rest": rest_amount,
        })
    return response_list


@app.get(
    "/receipts/{receipt_id}",
    response_model=schemas.ReceiptOut
)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(database.get_db),
    current_user=Depends(auth.get_current_user)
):
    r = crud.get_receipt_by_id(db, current_user.id, receipt_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    products = [
        {"name": it.name, "price": it.price, "quantity": it.quantity, "total": it.price * it.quantity}
        for it in r.items
    ]
    total_amount = sum(item['total'] for item in products)
    rest_amount = r.payment_amount - total_amount

    return {
        "id": r.id,
        "created_at": r.created_at,
        "products": products,
        "payment": {"type": r.payment_type, "amount": r.payment_amount},
        "total": total_amount,
        "rest": rest_amount,
    }


@app.get(
    "/public/receipts/{receipt_id}",
    response_class=PlainTextResponse
)
def public_receipt(
    receipt_id: int,
    width: int = Query(40, ge=20),
    db: Session = Depends(database.get_db)
):
    r = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    products = [
        {"name": it.name, "price": it.price, "quantity": it.quantity, "total": it.price * it.quantity}
        for it in r.items
    ]
    total_amount = sum(item['total'] for item in products)
    rest_amount = r.payment_amount - total_amount
    data = {
        "id": r.id,
        "created_at": r.created_at,
        "products": products,
        "payment": {"type": r.payment_type, "amount": r.payment_amount},
        "total": total_amount,
        "rest": rest_amount,
    }
    text = receipt_formatter.format_receipt(data, width)
    return text


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
