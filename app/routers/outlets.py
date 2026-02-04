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

@router.get("/outlets/", response_model=List[schemas.OutletResponse])
def read_outlets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    outlets = db.query(models.Outlet).filter(models.Outlet.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return outlets

@router.get("/outlets/{outlet_id}", response_model=schemas.OutletResponse)
def read_outlet(outlet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if outlet is None:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return outlet

@router.post("/outlets/", response_model=schemas.OutletResponse)
def create_outlet(outlet: schemas.OutletCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    outlet_data = outlet.dict()
    outlet_data["organization_id"] = current_user.organization_id
    db_outlet = models.Outlet(**outlet_data)
    db.add(db_outlet)
    db.commit()
    db.refresh(db_outlet)
    return db_outlet

@router.put("/outlets/{outlet_id}", response_model=schemas.OutletResponse)
def update_outlet(outlet_id: int, outlet: schemas.OutletUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_outlet is None:
        raise HTTPException(status_code=404, detail="Outlet not found")
    for key, value in outlet.dict(exclude_unset=True).items():
        setattr(db_outlet, key, value)
    db.commit()
    db.refresh(db_outlet)
    return db_outlet

@router.delete("/outlets/{outlet_id}")
def delete_outlet(outlet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_outlet is None:
        raise HTTPException(status_code=404, detail="Outlet not found")
    db.delete(db_outlet)
    db.commit()
    return {"message": "Outlet deleted"}

@router.get("/cashier-stations/", response_model=List[schemas.CashierStationResponse])
def read_cashier_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    stations = db.query(models.CashierStation).filter(models.CashierStation.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return stations

@router.get("/cashier-stations/{station_id}", response_model=schemas.CashierStationResponse)
def read_cashier_station(station_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    station = db.query(models.CashierStation).filter(models.CashierStation.id == station_id, models.CashierStation.organization_id == current_user.organization_id).first()
    if station is None:
        raise HTTPException(status_code=404, detail="Cashier Station not found")
    return station

@router.post("/cashier-stations/", response_model=schemas.CashierStationResponse)
def create_cashier_station(station: schemas.CashierStationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    station_data = station.dict()
    station_data["organization_id"] = current_user.organization_id
    db_station = models.CashierStation(**station_data)
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.put("/cashier-stations/{station_id}", response_model=schemas.CashierStationResponse)
def update_cashier_station(station_id: int, station: schemas.CashierStationUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_station = db.query(models.CashierStation).filter(models.CashierStation.id == station_id, models.CashierStation.organization_id == current_user.organization_id).first()
    if db_station is None:
        raise HTTPException(status_code=404, detail="Cashier Station not found")
    for key, value in station.dict(exclude_unset=True).items():
        setattr(db_station, key, value)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.delete("/cashier-stations/{station_id}")
def delete_cashier_station(station_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_station = db.query(models.CashierStation).filter(models.CashierStation.id == station_id, models.CashierStation.organization_id == current_user.organization_id).first()
    if db_station is None:
        raise HTTPException(status_code=404, detail="Cashier Station not found")
    db.delete(db_station)
    db.commit()
    return {"message": "Cashier Station deleted"}
