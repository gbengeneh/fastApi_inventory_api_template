from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..database import SessionLocal
from .. import models, schemas, auth
from ..printer_utils import print_receipt, print_invoice_pdf

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sales/", response_model=List[schemas.SaleResponse])
def read_sales(skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    query = db.query(models.Sale).filter(models.Sale.organization_id == current_user.organization_id)
    if customer_id is not None:
        query = query.filter(models.Sale.customer_id == customer_id)
    sales = query.offset(skip).limit(limit).all()
    return sales

@router.get("/sales/{sale_id}", response_model=schemas.SaleResponse)
def read_sale(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.post("/sales/", response_model=schemas.SaleResponse)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Role-based validation for cashier_station_id
    if current_user.role == "cashier":
        if sale.cashier_station_id is None:
            raise HTTPException(status_code=400, detail="cashier_station_id is required for cashiers")
    else:  # admin or manager
        if sale.cashier_station_id is not None:
            raise HTTPException(status_code=400, detail="cashier_station_id should not be provided for non-cashier users")

    # Create the sale first
    sale_data = sale.dict()
    sale_data["organization_id"] = current_user.organization_id
    items = sale_data.pop('items')
    payment_id = sale_data.pop('payment_id', None)

    # If payment_id is provided, validate it exists and belongs to user's organization
    if payment_id:
        payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == current_user.organization_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        sale_data['payment_id'] = payment_id

    db_sale = models.Sale(**sale_data)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    # Create sale items
    for item_data in items:
        item_data['sale_id'] = db_sale.id
        db_item = models.SaleItem(**item_data)
        db.add(db_item)

    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.put("/sales/{sale_id}", response_model=schemas.SaleResponse)
def update_sale(sale_id: int, sale: schemas.SaleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    for key, value in sale.dict(exclude_unset=True).items():
        setattr(db_sale, key, value)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.delete("/sales/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    db.delete(db_sale)
    db.commit()
    return {"message": "Sale deleted"}

@router.get("/sale-items/", response_model=List[schemas.SaleItemResponse])
def read_sale_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    items = db.query(models.SaleItem).join(models.Sale).filter(models.Sale.organization_id == current_user.organization_id).offset(skip).limit(limit).all()
    return items

@router.get("/sale-items/{item_id}", response_model=schemas.SaleItemResponse)
def read_sale_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    item = db.query(models.SaleItem).join(models.Sale).filter(models.SaleItem.id == item_id, models.Sale.organization_id == current_user.organization_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Sale Item not found")
    return item

@router.post("/sale-items/", response_model=schemas.SaleItemResponse)
def create_sale_item(item: schemas.SaleItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate that the sale belongs to the user's organization
    sale = db.query(models.Sale).filter(models.Sale.id == item.sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found or does not belong to your organization")
    db_item = models.SaleItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/sale-items/{item_id}", response_model=schemas.SaleItemResponse)
def update_sale_item(item_id: int, item: schemas.SaleItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_item = db.query(models.SaleItem).join(models.Sale).filter(models.SaleItem.id == item_id, models.Sale.organization_id == current_user.organization_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Sale Item not found")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/sale-items/{item_id}")
def delete_sale_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_item = db.query(models.SaleItem).join(models.Sale).filter(models.SaleItem.id == item_id, models.Sale.organization_id == current_user.organization_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Sale Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Sale Item deleted"}

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
    payment_data = payment.dict()
    payment_data["organization_id"] = current_user.organization_id

    # Calculate change for cash payments
    if payment.method == "cash" and payment.amount_tendered is not None:
        if payment.amount_tendered < payment.amount:
            raise HTTPException(status_code=400, detail="Amount tendered must be at least the payment amount")
        payment_data['change'] = payment.amount_tendered - payment.amount

    db_payment = models.Payment(**payment_data)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.put("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(payment_id: int, payment: schemas.PaymentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    for key, value in payment.dict(exclude_unset=True).items():
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

@router.get("/sales/{sale_id}/invoice")
def generate_invoice(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    sale = db.query(models.Sale).options(joinedload(models.Sale.items).joinedload(models.SaleItem.product), joinedload(models.Sale.outlet)).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Get default printer and template for the outlet
    default_printer = db.query(models.PrinterSettings).filter(
        models.PrinterSettings.outlet_id == sale.outlet_id,
        models.PrinterSettings.is_default == True
    ).first()

    default_template = db.query(models.InvoiceTemplate).filter(
        models.InvoiceTemplate.outlet_id == sale.outlet_id,
        models.InvoiceTemplate.is_default == True
    ).first()

    if not default_template:
        raise HTTPException(status_code=404, detail="Default template not configured for this outlet")

    # If no default printer, default to PDF printing
    if not default_printer:
        printer_type = "a4"
        printer_name = "PDF"
        settings = None
    else:
        printer_type = default_printer.printer_type
        printer_name = default_printer.printer_name
        settings = default_printer.settings

    # Generate invoice data (simplified for now)
    invoice_data = {
        "sale_id": sale.id,
        "outlet": {
            "name": sale.outlet.name,
            "address": sale.outlet.address,
            "phone": sale.outlet.phone,
            "email": sale.outlet.email
        },
        "total_amount": sale.total_amount,
        "discount": sale.discount,
        "tax": sale.tax,
        "net_total": sale.net_total,
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "total": item.total
            } for item in sale.items
        ],
        "printer_settings": {
            "type": printer_type,
            "name": printer_name,
            "settings": settings
        },
        "template": {
            "name": default_template.name,
            "header_text": default_template.header_text,
            "footer_text": default_template.footer_text
        }
    }

    return invoice_data

@router.post("/sales/{sale_id}/print")
def print_sale_invoice(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Print invoice for a sale using configured printer. Falls back to PDF if no printer configured."""
    sale = db.query(models.Sale).options(joinedload(models.Sale.items).joinedload(models.SaleItem.product), joinedload(models.Sale.outlet)).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.outlet is None:
        raise HTTPException(status_code=404, detail="Sale outlet not found")

    # Get default printer and template for the outlet
    default_printer = db.query(models.PrinterSettings).filter(
        models.PrinterSettings.outlet_id == sale.outlet_id,
        models.PrinterSettings.is_default == True
    ).first()

    default_template = db.query(models.InvoiceTemplate).filter(
        models.InvoiceTemplate.outlet_id == sale.outlet_id,
        models.InvoiceTemplate.is_default == True
    ).first()

    if not default_template:
        raise HTTPException(status_code=404, detail="Default template not configured for this outlet")

    # If no default printer, default to PDF printing
    if not default_printer:
        printer_type = "a4"
        printer_name = "PDF"
        settings = None
    else:
        printer_type = default_printer.printer_type
        printer_name = default_printer.printer_name
        settings = default_printer.settings

    # Prepare invoice data
    invoice_data = {
        "sale_id": sale.id,
        "outlet": {
            "name": sale.outlet.name,
            "address": sale.outlet.address,
            "phone": sale.outlet.phone,
            "email": sale.outlet.email
        },
        "total_amount": sale.total_amount,
        "discount": sale.discount,
        "tax": sale.tax,
        "net_total": sale.net_total,
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "total": item.total
            } for item in sale.items
        ],
        "template": {
            "header_text": default_template.header_text,
            "footer_text": default_template.footer_text
        }
    }

    # Print based on printer type
    if printer_type == "thermal":
        result = print_receipt(printer_name, invoice_data, settings)
    elif printer_type == "a4":
        result = print_invoice_pdf(printer_name, invoice_data, None)
    else:
        raise HTTPException(status_code=400, detail="Unsupported printer type")

    return result

@router.post("/sales/{sale_id}/payments/", response_model=schemas.SalePaymentResponse)
def create_sale_payment(sale_id: int, payment: schemas.SalePaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate sale exists and belongs to user's organization
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Validate payment exists and belongs to user's organization
    payment_record = db.query(models.Payment).filter(models.Payment.id == payment.payment_id, models.Payment.organization_id == current_user.organization_id).first()
    if not payment_record:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Create sale payment
    sale_payment_data = payment.dict()
    sale_payment_data['sale_id'] = sale_id
    db_sale_payment = models.SalePayment(**sale_payment_data)
    db.add(db_sale_payment)
    db.commit()
    db.refresh(db_sale_payment)
    return db_sale_payment

@router.get("/sales/{sale_id}/payments/", response_model=List[schemas.SalePaymentResponse])
def read_sale_payments(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate sale belongs to user's organization
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    sale_payments = db.query(models.SalePayment).filter(models.SalePayment.sale_id == sale_id).all()
    return sale_payments

@router.delete("/sales/{sale_id}/payments/{payment_id}")
def delete_sale_payment(sale_id: int, payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Validate sale belongs to user's organization
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id, models.Sale.organization_id == current_user.organization_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    sale_payment = db.query(models.SalePayment).join(models.Sale).filter(
        models.SalePayment.sale_id == sale_id,
        models.SalePayment.payment_id == payment_id,
        models.Sale.organization_id == current_user.organization_id
    ).first()
    if not sale_payment:
        raise HTTPException(status_code=404, detail="Sale payment not found")
    db.delete(sale_payment)
    db.commit()
    return {"message": "Sale payment deleted"}
