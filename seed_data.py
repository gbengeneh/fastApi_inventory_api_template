#!/usr/bin/env python3
"""
Seed script to create initial data in the database.
Run this script once to set up the initial categories, units, and other data.
"""

from app.database import SessionLocal
from app.models import Category, Unit, Outlet, Supplier, User, Product, Organization, Customer
from app.auth import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # Check if organization exists (should be created by client during setup)
        organization = db.query(Organization).first()
        if not organization:
            print("No organization found. Please create an organization first through the client setup.")
            return

        print(f"Using existing organization: {organization.name} (ID: {organization.id})")

        # Seed categories
        categories = [
            {"name": "Provision", "description": "General provision items"},
            {"name": "Kitchen", "description": "Kitchen supplies and utensils"},
            {"name": "Toiletries", "description": "Personal care and hygiene products"},
            {"name": "Gifts", "description": "Gift items and novelty products"},
            {"name": "Frozen", "description": "Frozen food items"}
        ]

        for cat_data in categories:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                cat_data["organization_id"] = organization.id
                category = Category(**cat_data)
                db.add(category)
                print(f"Added category: {cat_data['name']}")

        # Seed units
        units = [
            {"name": "Piece", "symbol": "pc"},
            {"name": "Kilogram", "symbol": "kg"},
            {"name": "Liter", "symbol": "L"},
            {"name": "Pack", "symbol": "pk"},
            {"name": "Box", "symbol": "bx"}
        ]

        for unit_data in units:
            unit = db.query(Unit).filter(Unit.name == unit_data["name"]).first()
            if not unit:
                unit = Unit(**unit_data)
                db.add(unit)
                print(f"Added unit: {unit_data['name']}")

        # Seed outlet
        outlet = db.query(Outlet).filter(Outlet.name == "Main Outlet").first()
        if not outlet:
            outlet = Outlet(
                organization_id=organization.id,
                name="Main Outlet",
                address="123 Main Street, City",
                phone="+1234567890",
                email="main@outlet.com"
            )
            db.add(outlet)
            db.commit()  # Commit the outlet so it's available for admin user
            print("Added outlet: Main Outlet")

        # Seed supplier
        supplier = db.query(Supplier).filter(Supplier.name == "Default Supplier").first()
        if not supplier:
            supplier = Supplier(
                organization_id=organization.id,
                name="Default Supplier",
                contact_person="John Doe",
                phone="+1234567890",
                email="supplier@example.com",
                address="456 Supplier Ave, City"
            )
            db.add(supplier)
            print("Added supplier: Default Supplier")

        # Seed default customer
        default_customer = db.query(Customer).filter(Customer.name == "Walk-in Customer").first()
        if not default_customer:
            default_customer = Customer(
                organization_id=organization.id,
                name="Walk-in Customer",
                phone="+1234567890",
                address="N/A"
            )
            db.add(default_customer)
            print("Added default customer: Walk-in Customer")

        # Seed admin user if not exists
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            admin_email = "admin@inventory.com"
            admin_password = "admin123"
            hashed_password = get_password_hash(admin_password)

            # Get the first outlet (Main Outlet)
            outlet = db.query(Outlet).first()
            if not outlet:
                print("No outlet found, cannot create admin user")
                return

            admin = User(
                organization_id=organization.id,
                name="Admin User",
                email=admin_email,
                password=hashed_password,
                role="admin",
                status="active",
                outlet_id=outlet.id
            )

            db.add(admin)
            print(f"Admin user created. Email: {admin_email}, Password: {admin_password}")

        # Seed products
        products = [
            # Provision
            {"name": "Rice", "category_id": 1, "unit_id": 2, "cost_price": 2.50, "selling_price": 3.00, "stock_quantity": 100, "reorder_level": 20, "description": "Premium long grain rice"},
            # Kitchen
            {"name": "Plate", "category_id": 2, "unit_id": 1, "cost_price": 2.00, "selling_price": 3.00, "stock_quantity": 100, "reorder_level": 20, "description": "Ceramic dinner plate"},
            # Toiletries
            {"name": "Toothpaste", "category_id": 3, "unit_id": 1, "cost_price": 2.00, "selling_price": 3.00, "stock_quantity": 60, "reorder_level": 12, "description": "Fluoride toothpaste tube"}
        ]

        for prod_data in products:
            product = db.query(Product).filter(Product.name == prod_data["name"]).first()
            if not product:
                prod_data["organization_id"] = organization.id
                product = Product(**prod_data)
                db.add(product)
                print(f"Added product: {prod_data['name']}")

        db.commit()
        print("Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
