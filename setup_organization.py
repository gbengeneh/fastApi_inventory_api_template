#!/usr/bin/env python3
"""
Setup script to create the initial organization for a new installation.
This should be run once during the client setup process.
"""

from app.database import SessionLocal
from app.models import Organization

def setup_organization(name: str, email: str, phone: str = None, address: str = None):
    """
    Create the initial organization for a new installation.

    Args:
        name: Organization name
        email: Organization email (must be unique)
        phone: Organization phone (optional)
        address: Organization address (optional)
    """
    db = SessionLocal()
    try:
        # Check if organization already exists
        existing_org = db.query(Organization).first()
        if existing_org:
            print(f"Organization already exists: {existing_org.name}")
            return existing_org

        # Create new organization
        organization = Organization(
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        print(f"Organization created successfully: {organization.name} (ID: {organization.id})")
        return organization

    except Exception as e:
        db.rollback()
        print(f"Error creating organization: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Example usage - replace with actual values from client setup
    import sys

    if len(sys.argv) < 3:
        print("Usage: python setup_organization.py <name> <email> [phone] [address]")
        sys.exit(1)

    name = sys.argv[1]
    email = sys.argv[2]
    phone = sys.argv[3] if len(sys.argv) > 3 else None
    address = sys.argv[4] if len(sys.argv) > 4 else None

    setup_organization(name, email, phone, address)
