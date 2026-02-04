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

@router.get("/categories/", response_model=List[schemas.CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    categories = db.query(models.Category).filter(models.Category.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    category = db.query(models.Category).filter(models.Category.id == category_id, models.Category.organization_id == current_user.organization_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    category_data = category.dict()
    category_data["organization_id"] = current_user.organization_id
    db_category = models.Category(**category_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_category = db.query(models.Category).filter(models.Category.id == category_id, models.Category.organization_id == current_user.organization_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_category = db.query(models.Category).filter(models.Category.id == category_id, models.Category.organization_id == current_user.organization_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted"}

@router.get("/units/", response_model=List[schemas.UnitResponse])
def read_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    units = db.query(models.Unit).offset(skip).limit(limit).all()
    return units

@router.get("/units/{unit_id}", response_model=schemas.UnitResponse)
def read_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.post("/units/", response_model=schemas.UnitResponse)
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_unit = models.Unit(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.put("/units/{unit_id}", response_model=schemas.UnitResponse)
def update_unit(unit_id: int, unit: schemas.UnitUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    for key, value in unit.dict(exclude_unset=True).items():
        setattr(db_unit, key, value)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.delete("/units/{unit_id}")
def delete_unit(unit_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(db_unit)
    db.commit()
    return {"message": "Unit deleted"}

@router.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    products = db.query(models.Product).filter(models.Product.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return products

@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.organization_id == current_user.organization_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    # Check if category exists
    category = db.query(models.Category).filter(models.Category.id == product.category_id, models.Category.organization_id == current_user.organization_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category with id {product.category_id} does not exist")

    # Check if unit exists
    unit = db.query(models.Unit).filter(models.Unit.id == product.unit_id).first()
    if not unit:
        raise HTTPException(status_code=400, detail=f"Unit with id {product.unit_id} does not exist")

    product_data = product.dict()
    product_data["organization_id"] = current_user.organization_id
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.organization_id == current_user.organization_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.organization_id == current_user.organization_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

@router.post("/products/bulk/", response_model=List[schemas.ProductResponse])
def create_products_bulk(products: List[schemas.ProductBulkCreate], db: Session = Depends(get_db), current_user: models.User = Depends(auth.check_role("admin"))):
    created_products = []
    errors = []

    for idx, product_data in enumerate(products):
        try:
            # Check if category exists
            category = db.query(models.Category).filter(models.Category.id == product_data.category_id, models.Category.organization_id == current_user.organization_id).first()
            if not category:
                errors.append({"index": idx, "error": f"Category with id {product_data.category_id} does not exist"})
                continue

            # Check if unit exists
            unit = db.query(models.Unit).filter(models.Unit.id == product_data.unit_id).first()
            if not unit:
                errors.append({"index": idx, "error": f"Unit with id {product_data.unit_id} does not exist"})
                continue

            # tax_rate is already in decimal format (0-1), default to 0.0 if None
            product_dict = product_data.dict()
            product_dict['tax_rate'] = product_data.tax_rate if product_data.tax_rate is not None else 0.0
            product_dict["organization_id"] = current_user.organization_id

            db_product = models.Product(**product_dict)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            created_products.append(db_product)

        except Exception as e:
            db.rollback()
            errors.append({"index": idx, "error": str(e)})

    if errors:
        raise HTTPException(status_code=400, detail={"message": "Some products failed to create", "errors": errors, "created_count": len(created_products)})

    return created_products
