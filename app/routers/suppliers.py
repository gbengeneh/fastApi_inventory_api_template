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

@router.get("/suppliers/", response_model=List[schemas.SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    suppliers = db.query(models.Supplier).filter(models.Supplier.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return suppliers

@router.get("/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def read_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id, models.Supplier.organization_id == current_user.organization_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("/suppliers/", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    supplier_data = supplier.dict()
    supplier_data["organization_id"] = current_user.organization_id
    db_supplier = models.Supplier(**supplier_data)
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.put("/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def update_supplier(supplier_id: int, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id, models.Supplier.organization_id == current_user.organization_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in supplier.dict(exclude_unset=True).items():
        setattr(db_supplier, key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.check_role("admin"))):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id, models.Supplier.organization_id == current_user.organization_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(db_supplier)
    db.commit()
    return {"message": "Supplier deleted"}

@router.get("/purchases/", response_model=List[schemas.PurchaseResponse])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    purchases = db.query(models.Purchase).offset(skip).limit(limit).all()
    return purchases

@router.get("/purchases/{purchase_id}", response_model=schemas.PurchaseResponse)
def read_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.post("/purchases/", response_model=schemas.PurchaseResponse)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Create the purchase
    purchase_data = purchase.dict(exclude={'items'})
    purchase_data['created_by'] = current_user.id
    purchase_data['organization_id'] = current_user.organization_id
    # Ensure invoice_number is None if empty string to avoid unique constraint issues
    if purchase_data.get('invoice_number') == '':
        purchase_data['invoice_number'] = None
    db_purchase = models.Purchase(**purchase_data)
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    # Create purchase items and update product stock
    total_amount = 0.0
    for item in purchase.items:
        # Create purchase item
        db_item = models.PurchaseItem(
            purchase_id=db_purchase.id,
            product_id=item.product_id,
            quantity=item.quantity,
            cost_price=item.cost_price
        )
        db.add(db_item)

        # Update product stock and cost_price
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        product.stock_quantity += item.quantity
        product.cost_price = item.cost_price  # Update cost price to the new purchase price

        total_amount += item.quantity * item.cost_price

    # Update total amount
    db_purchase.total_amount = total_amount
    db.commit()

    return db_purchase

@router.put("/purchases/{purchase_id}", response_model=schemas.PurchaseResponse)
def update_purchase(purchase_id: int, purchase: schemas.PurchaseUpdate, db: Session = Depends(get_db)):
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    for key, value in purchase.dict(exclude_unset=True).items():
        setattr(db_purchase, key, value)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

@router.delete("/purchases/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    db.delete(db_purchase)
    db.commit()
    return {"message": "Purchase deleted"}

@router.get("/purchase-items/", response_model=List[schemas.PurchaseItemResponse])
def read_purchase_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.PurchaseItem).offset(skip).limit(limit).all()
    return items

@router.get("/purchase-items/{item_id}", response_model=schemas.PurchaseItemResponse)
def read_purchase_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.PurchaseItem).filter(models.PurchaseItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    return item

@router.post("/purchase-items/", response_model=schemas.PurchaseItemResponse)
def create_purchase_item(item: schemas.PurchaseItemCreate, db: Session = Depends(get_db)):
    db_item = models.PurchaseItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/purchase-items/{item_id}", response_model=schemas.PurchaseItemResponse)
def update_purchase_item(item_id: int, item: schemas.PurchaseItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.PurchaseItem).filter(models.PurchaseItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/purchase-items/{item_id}")
def delete_purchase_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.PurchaseItem).filter(models.PurchaseItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Purchase Item deleted"}
