#!/usr/bin/env python3
"""
Script to create or reset an admin user in the database.
Run this script to set up or reset the admin account.
"""

from app.database import SessionLocal
from app.models import User, Outlet
from app.auth import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@inventory.com"
        admin_password = "admin123"  # Change this to a secure password
        hashed_password = get_password_hash(admin_password)

        # Get the first outlet
        outlet = db.query(Outlet).first()
        if not outlet:
            print("No outlet found, cannot create/reset admin user")
            return

        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if admin_user:
            # Reset password for existing admin
            admin_user.password = hashed_password
            db.commit()
            print(f"Admin user password reset successfully. Email: {admin_email}, Password: {admin_password}")
        else:
            # Create new admin user
            admin = User(
                name="Admin User",
                email=admin_email,
                password=hashed_password,
                role="admin",
                status="active",
                outlet_id=outlet.id
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin user created successfully. Email: {admin_email}, Password: {admin_password}")

        print("Please change the password after first login.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding/resetting admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
