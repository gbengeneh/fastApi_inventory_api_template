from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from .. import models, schemas, auth
from ..printer_utils import get_installed_printers

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/printer-settings/", response_model=List[schemas.PrinterSettingsResponse])
def read_printer_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    settings = db.query(models.PrinterSettings).join(models.Outlet).filter(models.Outlet.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return settings

@router.get("/printer-settings/{setting_id}", response_model=schemas.PrinterSettingsResponse)
def read_printer_setting(setting_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    setting = db.query(models.PrinterSettings).join(models.Outlet).filter(models.PrinterSettings.id == setting_id, models.Outlet.organization_id == current_user.organization_id).first()
    if setting is None:
        raise HTTPException(status_code=404, detail="Printer setting not found")
    return setting

@router.post("/printer-settings/", response_model=schemas.PrinterSettingsResponse)
def create_printer_setting(setting: schemas.PrinterSettingsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate outlet belongs to user's organization
    outlet = db.query(models.Outlet).filter(models.Outlet.id == setting.outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    # Ensure only one default per outlet per type
    if setting.is_default:
        existing_default = db.query(models.PrinterSettings).filter(
            models.PrinterSettings.outlet_id == setting.outlet_id,
            models.PrinterSettings.printer_type == setting.printer_type,
            models.PrinterSettings.is_default == True
        ).first()
        if existing_default:
            existing_default.is_default = False
            db.commit()
    db_setting = models.PrinterSettings(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.put("/printer-settings/{setting_id}", response_model=schemas.PrinterSettingsResponse)
def update_printer_setting(setting_id: int, setting: schemas.PrinterSettingsUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_setting = db.query(models.PrinterSettings).join(models.Outlet).filter(models.PrinterSettings.id == setting_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Printer setting not found")
    # Handle default logic
    if setting.is_default is True:
        existing_default = db.query(models.PrinterSettings).filter(
            models.PrinterSettings.outlet_id == db_setting.outlet_id,
            models.PrinterSettings.printer_type == db_setting.printer_type,
            models.PrinterSettings.is_default == True,
            models.PrinterSettings.id != setting_id
        ).first()
        if existing_default:
            existing_default.is_default = False
    for key, value in setting.dict(exclude_unset=True).items():
        setattr(db_setting, key, value)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.delete("/printer-settings/{setting_id}")
def delete_printer_setting(setting_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_setting = db.query(models.PrinterSettings).join(models.Outlet).filter(models.PrinterSettings.id == setting_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Printer setting not found")
    db.delete(db_setting)
    db.commit()
    return {"message": "Printer setting deleted"}

@router.get("/invoice-templates/", response_model=List[schemas.InvoiceTemplateResponse])
def read_invoice_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    templates = db.query(models.InvoiceTemplate).join(models.Outlet).filter(models.Outlet.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return templates

@router.get("/invoice-templates/{template_id}", response_model=schemas.InvoiceTemplateResponse)
def read_invoice_template(template_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    template = db.query(models.InvoiceTemplate).join(models.Outlet).filter(models.InvoiceTemplate.id == template_id, models.Outlet.organization_id == current_user.organization_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Invoice template not found")
    return template

@router.post("/invoice-templates/", response_model=schemas.InvoiceTemplateResponse)
def create_invoice_template(template: schemas.InvoiceTemplateCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate outlet belongs to user's organization
    outlet = db.query(models.Outlet).filter(models.Outlet.id == template.outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    # Ensure only one default per outlet
    if template.is_default:
        existing_default = db.query(models.InvoiceTemplate).filter(
            models.InvoiceTemplate.outlet_id == template.outlet_id,
            models.InvoiceTemplate.is_default == True
        ).first()
        if existing_default:
            existing_default.is_default = False
            db.commit()
    db_template = models.InvoiceTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.put("/invoice-templates/{template_id}", response_model=schemas.InvoiceTemplateResponse)
def update_invoice_template(template_id: int, template: schemas.InvoiceTemplateUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_template = db.query(models.InvoiceTemplate).join(models.Outlet).filter(models.InvoiceTemplate.id == template_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Invoice template not found")
    # Handle default logic
    if template.is_default is True:
        existing_default = db.query(models.InvoiceTemplate).filter(
            models.InvoiceTemplate.outlet_id == db_template.outlet_id,
            models.InvoiceTemplate.is_default == True,
            models.InvoiceTemplate.id != template_id
        ).first()
        if existing_default:
            existing_default.is_default = False
    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/invoice-templates/{template_id}")
def delete_invoice_template(template_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_template = db.query(models.InvoiceTemplate).join(models.Outlet).filter(models.InvoiceTemplate.id == template_id, models.Outlet.organization_id == current_user.organization_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Invoice template not found")
    db.delete(db_template)
    db.commit()
    return {"message": "Invoice template deleted"}

@router.get("/outlets/{outlet_id}/default-printer", response_model=schemas.PrinterSettingsResponse)
def get_default_printer(outlet_id: int, printer_type: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate outlet belongs to user's organization
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    setting = db.query(models.PrinterSettings).filter(
        models.PrinterSettings.outlet_id == outlet_id,
        models.PrinterSettings.printer_type == printer_type,
        models.PrinterSettings.is_default == True
    ).first()
    if setting is None:
        raise HTTPException(status_code=404, detail="Default printer not found")
    return setting

@router.get("/outlets/{outlet_id}/default-template", response_model=schemas.InvoiceTemplateResponse)
def get_default_template(outlet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate outlet belongs to user's organization
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id, models.Outlet.organization_id == current_user.organization_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    template = db.query(models.InvoiceTemplate).filter(
        models.InvoiceTemplate.outlet_id == outlet_id,
        models.InvoiceTemplate.is_default == True
    ).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Default template not found")
    return template

@router.get("/printers/installed")
def get_installed_printers_endpoint():
    """Get list of installed printers on the system."""
    return {"printers": get_installed_printers()}
