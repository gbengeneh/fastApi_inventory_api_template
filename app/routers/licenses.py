# licenses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..database import get_db
from ..models import Organization
from datetime import datetime, timedelta
import jwt

# Secret key used to sign license keys (must match the website)
SECRET_KEY = "INVENTORY_BOSS_SECRET_KEY_HERE"
ALGORITHM = "HS256"

router = APIRouter(prefix="/licenses", tags=["licenses"])

# -------------------------------
# 1️⃣ VERIFY / ACTIVATE LICENSE
# -------------------------------
@router.post("/verify")
def verify_license(
    license_key: str = Query(...),
    email: str = Query(...),
    organization_name: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Verify a license key locally.
    Checks that:
      - JWT is valid and signature correct
      - License not expired
      - License email + org name match the local organization
    """
    try:
        payload = jwt.decode(license_key, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(400, "License has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(400, "Invalid license key")

    license_email = payload.get("email")
    license_org_name = payload.get("organization_name")
    expires_at_str = payload.get("expires_at")

    if not license_email or not license_org_name or not expires_at_str:
        raise HTTPException(400, "Invalid license payload")

    expires_at = datetime.fromisoformat(expires_at_str)

    if expires_at < datetime.utcnow():
        raise HTTPException(400, "License has expired")

    # Lookup organization in local DB (case-insensitive)
    organization = db.query(Organization).filter(
        func.lower(Organization.email) == func.lower(email),
        func.lower(Organization.name) == func.lower(organization_name)
    ).first()

    if not organization:
        raise HTTPException(404, "Organization not found")

    # Ensure license belongs to this organization
    if license_email != organization.email or license_org_name != organization.name:
        raise HTTPException(400, "License does not match this organization")

    # Activate organization
    organization.is_verified = True
    organization.status = "verified"
    db.commit()

    return {
        "message": "License verified successfully",
        "organization_id": organization.id,
        "expires_at": expires_at.isoformat()
    }

# -------------------------------
# 2️⃣ VALIDATE LICENSE
# -------------------------------
@router.post("/validate")
def validate_license(
    license_key: str = Query(...),
    email: str = Query(...),
    organization_name: str = Query(...),
):
    """
    Validates the license key without modifying DB.
    Returns valid: True/False and expires_at.
    """
    try:
        payload = jwt.decode(license_key, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"valid": False, "message": "License expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "message": "Invalid license key"}

    license_email = payload.get("email")
    license_org_name = payload.get("organization_name")
    expires_at_str = payload.get("expires_at")
    expires_at = datetime.fromisoformat(expires_at_str)

    valid = (
        license_email == email and
        license_org_name == organization_name and
        expires_at >= datetime.utcnow()
    )

    return {
        "valid": valid,
        "expires_at": expires_at.isoformat()
    }

# -------------------------------
# 3️⃣ CHECK EXPIRATION
# -------------------------------
@router.post("/check_expiration")
def check_expiration(
    license_key: str = Query(...),
):
    """
    Check if the license has expired.
    """
    try:
        payload = jwt.decode(license_key, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"expired": True}
    except jwt.InvalidTokenError:
        return {"expired": True}

    expires_at_str = payload.get("expires_at")
    expires_at = datetime.fromisoformat(expires_at_str)
    expired = expires_at < datetime.utcnow()

    return {
        "expired": expired,
        "expires_at": expires_at.isoformat()
    }

# -------------------------------
# 4️⃣ RENEW LICENSE
# -------------------------------
@router.post("/renew")
def renew_license(
    license_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Renew the license by generating a new expiration date.
    In this offline-first approach, the new license key must be generated on the website
    and pasted here by the user, then verified.
    """
    try:
        payload = jwt.decode(license_key, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(400, "Invalid license key")

    expires_at_str = payload.get("expires_at")
    expires_at = datetime.fromisoformat(expires_at_str)

    return {
        "message": "Renewal must be done on the website to generate a new license key",
        "current_expires_at": expires_at.isoformat()
    }
