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

@router.get("/users/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")
    users = db.query(models.User).filter(models.User.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    user = db.query(models.User).filter(models.User.id == user_id, models.User.organization_id == current_user.organization_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Handle outlet_id: if not provided, use the first available outlet for the organization
    if user.outlet_id is None:
        outlet = db.query(models.Outlet).filter(models.Outlet.organization_id == current_user.organization_id).first()
        if not outlet:
            raise HTTPException(status_code=404, detail="No outlets available for this organization")
        user.outlet_id = outlet.id
    else:
        # Verify outlet exists and belongs to the organization
        outlet = db.query(models.Outlet).filter(models.Outlet.id == user.outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found or does not belong to this organization")

    # Hash the password before saving
    hashed_password = auth.get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["organization_id"] = current_user.organization_id
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.organization_id == current_user.organization_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    if "email" in update_data:
        existing_user = db.query(models.User).filter(models.User.email == update_data["email"], models.User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
    for key, value in update_data.items():
        if key == "password":
            value = auth.get_password_hash(value)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.organization_id == current_user.organization_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/activity-logs/", response_model=List[schemas.UserActivityLogResponse])
def read_activity_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")
    logs = db.query(models.UserActivityLog).filter(models.UserActivityLog.user_id.in_(
        db.query(models.User.id).filter(models.User.organization_id == current_user.organization_id)
    )).offset(skip).limit(limit).all()
    return logs

@router.post("/activity-logs/", response_model=schemas.UserActivityLogResponse)
def create_activity_log(log: schemas.UserActivityLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Verify the user belongs to the organization
    user = db.query(models.User).filter(models.User.id == log.user_id, models.User.organization_id == current_user.organization_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")
    db_log = models.UserActivityLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
