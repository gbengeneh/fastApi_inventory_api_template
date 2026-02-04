from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Organization
from ..schemas import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from ..auth import get_current_user
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seed_data import seed_data  # Import the seed function

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=OrganizationResponse)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = None  # Make auth optional for initial setup
):
    # Check if any organization already exists (distributed app - only one organization per installation)
    existing_org = db.query(Organization).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization already exists. Only one organization is allowed per installation.")

    # Check if organization with same email exists (additional check)
    existing_org_email = db.query(Organization).filter(Organization.email == organization.email).first()
    if existing_org_email:
        raise HTTPException(status_code=400, detail="Organization with this email already exists")

    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    # Automatically seed initial data after organization creation
    try:
        seed_data()
        print(f"Initial data seeded successfully for organization: {db_organization.name}")
    except Exception as e:
        print(f"Warning: Failed to seed initial data: {e}")
        # Don't fail the organization creation if seeding fails

    return db_organization

@router.get("/", response_model=List[OrganizationResponse])
def read_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
def read_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if email is being updated and if it conflicts
    if organization_update.email and organization_update.email != organization.email:
        existing_org = db.query(Organization).filter(Organization.email == organization_update.email).first()
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization with this email already exists")

    for key, value in organization_update.dict(exclude_unset=True).items():
        setattr(organization, key, value)

    db.commit()
    db.refresh(organization)
    return organization

@router.delete("/{organization_id}")
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(organization)
    db.commit()
    return {"message": "Organization deleted successfully"}
