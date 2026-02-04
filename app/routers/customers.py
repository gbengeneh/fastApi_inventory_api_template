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

# ✅ Clean paths: just "/" or "/{id}"
@router.get("/", response_model=List[schemas.CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    customers = db.query(models.Customer).filter(models.Customer.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.organization_id == current_user.organization_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    customer_data = customer.dict()
    customer_data["organization_id"] = current_user.organization_id
    db_customer = models.Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.organization_id == current_user.organization_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in customer.dict(exclude_unset=True).items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.organization_id == current_user.organization_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted"}
