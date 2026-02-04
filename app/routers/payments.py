from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from .. import models, schemas, auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/payments/", response_model=List[schemas.PaymentResponse])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    payments = db.query(models.Payment).filter(models.Payment.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return payments

@router.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def read_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/payments/", response_model=schemas.PaymentResponse)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Calculate change if amount_tendered is provided
    change = None
    if payment.amount_tendered is not None:
        change = payment.amount_tendered - payment.amount
        if change < 0:
            raise HTTPException(status_code=400, detail="Amount tendered is less than payment amount")

    db_payment = models.Payment(
        payment_ref=payment.payment_ref,
        related_type=payment.related_type,
        related_id=payment.related_id,
        amount=payment.amount,
        amount_tendered=payment.amount_tendered,
        change=change,
        method=payment.method,
        user_id=payment.user_id,
        outlet_id=payment.outlet_id,
        organization_id=current_user.organization_id
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.put("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(payment_id: int, payment: schemas.PaymentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_data = payment.dict(exclude_unset=True)
    if 'amount_tendered' in update_data:
        amount_tendered = update_data['amount_tendered']
        amount = update_data.get('amount', db_payment.amount)
        update_data['change'] = amount_tendered - amount
        if update_data['change'] < 0:
            raise HTTPException(status_code=400, detail="Amount tendered is less than payment amount")

    for key, value in update_data.items():
        setattr(db_payment, key, value)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return {"message": "Payment deleted"}

@router.get("/sale-payments/", response_model=List[schemas.SalePaymentResponse])
def read_sale_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    sale_payments = db.query(models.SalePayment).join(models.Sale).filter(models.Sale.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return sale_payments

@router.get("/sale-payments/{sale_payment_id}", response_model=schemas.SalePaymentResponse)
def read_sale_payment(sale_payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    sale_payment = db.query(models.SalePayment).join(models.Sale).filter(models.SalePayment.id == sale_payment_id, models.Sale.organization_id == current_user.organization_id).first()
    if sale_payment is None:
        raise HTTPException(status_code=404, detail="Sale payment not found")
    return sale_payment

@router.post("/sales/{sale_id}/payments/", response_model=schemas.SalePaymentResponse)
def create_sale_payment(sale_id: int, sale_payment: schemas.SalePaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Verify sale exists
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Verify payment exists
    payment = db.query(models.Payment).filter(models.Payment.id == sale_payment.payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify sale_id matches
    if sale_payment.sale_id != sale_id:
        raise HTTPException(status_code=400, detail="Sale ID mismatch")

    db_sale_payment = models.SalePayment(**sale_payment.dict())
    db.add(db_sale_payment)
    db.commit()
    db.refresh(db_sale_payment)
    return db_sale_payment

@router.put("/sale-payments/{sale_payment_id}", response_model=schemas.SalePaymentResponse)
def update_sale_payment(sale_payment_id: int, sale_payment: schemas.SalePaymentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_sale_payment = db.query(models.SalePayment).join(models.Sale).filter(models.SalePayment.id == sale_payment_id, models.Sale.organization_id == current_user.organization_id).first()
    if db_sale_payment is None:
        raise HTTPException(status_code=404, detail="Sale payment not found")
    for key, value in sale_payment.dict(exclude_unset=True).items():
        setattr(db_sale_payment, key, value)
    db.commit()
    db.refresh(db_sale_payment)
    return db_sale_payment

@router.delete("/sales/{sale_id}/payments/{payment_id}")
def delete_sale_payment(sale_id: int, payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_sale_payment = db.query(models.SalePayment).join(models.Sale).filter(
        models.SalePayment.sale_id == sale_id,
        models.SalePayment.payment_id == payment_id,
        models.Sale.organization_id == current_user.organization_id
    ).first()
    if db_sale_payment is None:
        raise HTTPException(status_code=404, detail="Sale payment not found")
    db.delete(db_sale_payment)
    db.commit()
    return {"message": "Sale payment deleted"}
