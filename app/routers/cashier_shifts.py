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

@router.get("/cashier-shifts/", response_model=List[schemas.CashierShiftResponse])
def read_cashier_shifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    shifts = db.query(models.CashierShift).filter(models.CashierShift.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return shifts

@router.get("/cashier-shifts/{shift_id}", response_model=schemas.CashierShiftResponse)
def read_cashier_shift(shift_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    shift = db.query(models.CashierShift).filter(models.CashierShift.id == shift_id, models.CashierShift.organization_id == current_user.organization_id).first()
    if shift is None:
        raise HTTPException(status_code=404, detail="Cashier shift not found")
    return shift

@router.post("/cashier-shifts/", response_model=schemas.CashierShiftResponse)
def create_cashier_shift(shift: schemas.CashierShiftCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == shift.user_id, models.User.organization_id == current_user.organization_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"User with id {shift.user_id} does not exist")

    # Check if cashier station exists
    station = db.query(models.CashierStation).filter(models.CashierStation.id == shift.cashier_station_id, models.CashierStation.organization_id == current_user.organization_id).first()
    if not station:
        raise HTTPException(status_code=400, detail=f"Cashier station with id {shift.cashier_station_id} does not exist")

    # Check if outlet exists
    outlet = db.query(models.Outlet).filter(models.Outlet.id == shift.outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if not outlet:
        raise HTTPException(status_code=400, detail=f"Outlet with id {shift.outlet_id} does not exist")

    # Check if user already has an open shift
    open_shift = db.query(models.CashierShift).filter(
        models.CashierShift.user_id == shift.user_id,
        models.CashierShift.status == "open"
    ).first()
    if open_shift:
        raise HTTPException(status_code=400, detail="User already has an open shift")

    db_shift = models.CashierShift(**shift.dict(), organization_id=current_user.organization_id)
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift

@router.put("/cashier-shifts/{shift_id}", response_model=schemas.CashierShiftResponse)
def update_cashier_shift(shift_id: int, shift: schemas.CashierShiftUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_shift = db.query(models.CashierShift).filter(models.CashierShift.id == shift_id, models.CashierShift.organization_id == current_user.organization_id).first()
    if db_shift is None:
        raise HTTPException(status_code=404, detail="Cashier shift not found")

    # If closing the shift, set end_time
    if shift.status == "closed" and db_shift.status == "open":
        from datetime import datetime
        db_shift.end_time = datetime.utcnow()

    for key, value in shift.dict(exclude_unset=True).items():
        setattr(db_shift, key, value)
    db.commit()
    db.refresh(db_shift)
    return db_shift

@router.delete("/cashier-shifts/{shift_id}")
def delete_cashier_shift(shift_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_shift = db.query(models.CashierShift).filter(models.CashierShift.id == shift_id, models.CashierShift.organization_id == current_user.organization_id).first()
    if db_shift is None:
        raise HTTPException(status_code=404, detail="Cashier shift not found")
    db.delete(db_shift)
    db.commit()
    return {"message": "Cashier shift deleted"}
