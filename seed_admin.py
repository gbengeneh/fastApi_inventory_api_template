#!/usr/bin/env python3
"""
Seed script to create an initial admin user in the database.
Run this script once to set up the admin account.
"""

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.role == "admin").first()
        if admin_user:
            print("Admin user already exists.")
            return

        # Create admin user
        admin_email = "admin@inventory.com"
        admin_password = "admin123"  # Change this to a secure password
        hashed_password = get_password_hash(admin_password)

        admin = User(
            name="Admin User",
            email=admin_email,
            password=hashed_password,
            role="admin",
            status="active"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created successfully. Email: {admin_email}, Password: {admin_password}")
        print("Please change the password after first login.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
