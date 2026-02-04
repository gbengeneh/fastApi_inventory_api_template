from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
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

@router.get("/purchases/", response_model=List[schemas.PurchaseResponse])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    purchases = db.query(models.Purchase).filter(models.Purchase.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return purchases

@router.get("/purchases/{purchase_id}", response_model=schemas.PurchaseResponse)
def read_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id, models.Purchase.organization_id == current_user.organization_id).first()
    if purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.post("/purchases/", response_model=schemas.PurchaseResponse)
def create_purchase(purchase: schemas.PurchaseCreate, current_user: models.User = Depends(auth.check_role("admin")), db: Session = Depends(get_db)):
    # Set organization_id from current user
    purchase_data = purchase.dict()
    purchase_data['organization_id'] = current_user.organization_id
    try:
        print("Starting purchase creation")
        # Create the purchase first
        purchase_data = purchase.dict()
        items = purchase_data.pop('items')
        # Set created_by and outlet_id from current user
        purchase_data['created_by'] = current_user.id
        purchase_data['outlet_id'] = current_user.outlet_id
        purchase_data['organization_id'] = current_user.organization_id
        print(f"Purchase data: {purchase_data}")
        db_purchase = models.Purchase(**purchase_data)
        db.add(db_purchase)
        print("Purchase object created")

        # Process each item and update product prices
        for item_data in items:
            print(f"Processing item: {item_data}")
            product = db.query(models.Product).filter(models.Product.id == item_data['product_id'], models.Product.organization_id == current_user.organization_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_data['product_id']} not found")
            print(f"Found product: {product.name}, current cost: {product.cost_price}, selling: {product.selling_price}, stock: {product.stock_quantity}")

            # Update product cost_price and selling_price with the provided selling_price
            product.cost_price = item_data['cost_price']
            product.selling_price = item_data['selling_price']

            # Update stock quantity
            product.stock_quantity += item_data['quantity']
            db.add(product)
            print(f"Updated product cost: {product.cost_price}, selling: {product.selling_price}, stock: {product.stock_quantity}")

            # Create purchase item (include selling_price as it's now stored in PurchaseItem)
            db_item = models.PurchaseItem(
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                cost_price=item_data['cost_price'],
                markup_percentage=item_data['markup_percentage'],
                selling_price=item_data['selling_price']
            )
            db_purchase.items.append(db_item)
            db.add(db_item)
            print(f"Added purchase item")

        print("About to commit")
        db.commit()
        print("Committed")
        db.refresh(db_purchase)
        print("Refreshed")
        print(f"Purchase created with id: {db_purchase.id}")
        print("Purchase creation successful")
        return db_purchase
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"Database integrity error: {str(e)}")
        if "UNIQUE constraint" in str(e) or "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="Purchase with this invoice number already exists")
        elif "FOREIGN KEY constraint" in str(e) or "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid reference: supplier, outlet, or user does not exist")
        else:
            raise HTTPException(status_code=400, detail=f"Database constraint violation: {str(e)}")
    except DataError as e:
        db.rollback()
        print(f"Data error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format or value exceeds allowed limits")
    except ValueError as e:
        db.rollback()
        print(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        print(f"Unexpected exception during purchase creation: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error during purchase creation: {str(e)}")

@router.put("/purchases/{purchase_id}", response_model=schemas.PurchaseResponse)
def update_purchase(purchase_id: int, purchase: schemas.PurchaseUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id, models.Purchase.organization_id == current_user.organization_id).first()
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    for key, value in purchase.dict(exclude_unset=True).items():
        setattr(db_purchase, key, value)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

@router.delete("/purchases/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id, models.Purchase.organization_id == current_user.organization_id).first()
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    db.delete(db_purchase)
    db.commit()
    return {"message": "Purchase deleted"}

@router.get("/purchase-items/", response_model=List[schemas.PurchaseItemResponse])
def read_purchase_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    items = db.query(models.PurchaseItem).join(models.Purchase).filter(models.Purchase.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return items

@router.get("/purchase-items/{item_id}", response_model=schemas.PurchaseItemResponse)
def read_purchase_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    item = db.query(models.PurchaseItem).join(models.Purchase).filter(models.PurchaseItem.id == item_id, models.Purchase.organization_id == current_user.organization_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    return item

@router.put("/purchase-items/{item_id}", response_model=schemas.PurchaseItemResponse)
def update_purchase_item(item_id: int, item: schemas.PurchaseItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_item = db.query(models.PurchaseItem).join(models.Purchase).filter(models.PurchaseItem.id == item_id, models.Purchase.organization_id == current_user.organization_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/purchase-items/{item_id}")
def delete_purchase_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_item = db.query(models.PurchaseItem).join(models.Purchase).filter(models.PurchaseItem.id == item_id, models.Purchase.organization_id == current_user.organization_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Purchase Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Purchase Item deleted"}
