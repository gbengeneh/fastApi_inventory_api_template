from app.database import SessionLocal
from app import models

db = SessionLocal()
try:
    # Create the purchase
    purchase = models.Purchase(organization_id=1, supplier_id=1, outlet_id=1, total_amount=100.0, created_by=1)
    db.add(purchase)

    # Assume product with id=1 exists; update its prices and stock as per router logic
    product = db.query(models.Product).filter(models.Product.id == 1).first()
    if not product:
        raise Exception("Product with id=1 not found")

    # Update product cost_price, selling_price, stock_quantity
    product.cost_price = 10.0
    product.selling_price = 15.0
    product.stock_quantity += 10

    # Create purchase item
    item = models.PurchaseItem(
        product_id=1,
        quantity=10,
        cost_price=10.0,
        markup_percentage=0.0,
        selling_price=15.0
    )
    purchase.items.append(item)
    db.add(item)

    db.commit()
    print('Purchase with items created successfully')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
