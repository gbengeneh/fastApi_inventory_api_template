from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .database import get_db, get_central_db, get_db_status, supabase
from .models import (
    Organization, License, User, Outlet, Product, Supplier, Purchase, PurchaseItem,
    Sale, SaleItem, Payment, UserActivityLog, PrinterSettings, InvoiceTemplate,
    SalePayment, CashierShift, Category, Unit, CashierStation, Customer
)
import logging

logger = logging.getLogger(__name__)

def sync_data():
    """Sync all local data to central database (PostgreSQL or Supabase) if online."""
    connection_type = get_db_status()
    if connection_type == "offline":
        # Suppress info log to avoid cluttering logs during periodic sync
        # logger.info("Offline: Skipping sync to central database.")
        return

    logger.info(f"Online ({connection_type}): Starting sync to central database.")

    local_db = next(get_db())

    try:
        if connection_type == "postgresql":
            central_db = next(get_central_db())
            # Sync organizations
            sync_table_sqlalchemy(local_db, central_db, Organization)

            # Sync licenses
            sync_table_sqlalchemy(local_db, central_db, License)

            # Sync users
            sync_table_sqlalchemy(local_db, central_db, User)

            # Sync outlets
            sync_table_sqlalchemy(local_db, central_db, Outlet)

            # Sync categories and units (if not already synced)
            sync_table_sqlalchemy(local_db, central_db, Category)
            sync_table_sqlalchemy(local_db, central_db, Unit)

            # Sync products
            sync_table_sqlalchemy(local_db, central_db, Product)

            # Sync suppliers
            sync_table_sqlalchemy(local_db, central_db, Supplier)
            
            # Sync customers
            sync_table_sqlalchemy(local_db, central_db, Customer)

            # Sync purchases and items
            sync_table_sqlalchemy(local_db, central_db, Purchase)
            sync_table_sqlalchemy(local_db, central_db, PurchaseItem)

            # Sync sales and items
            sync_table_sqlalchemy(local_db, central_db, Sale)
            sync_table_sqlalchemy(local_db, central_db, SaleItem)

            # Sync payments
            sync_table_sqlalchemy(local_db, central_db, Payment)

            # Sync other tables
            sync_table_sqlalchemy(local_db, central_db, UserActivityLog)
            sync_table_sqlalchemy(local_db, central_db, PrinterSettings)
            sync_table_sqlalchemy(local_db, central_db, InvoiceTemplate)
            sync_table_sqlalchemy(local_db, central_db, SalePayment)
            sync_table_sqlalchemy(local_db, central_db, CashierShift)
            sync_table_sqlalchemy(local_db, central_db, CashierStation)

            central_db.commit()
            central_db.close()
        elif connection_type == "supabase":
            # Sync in order to respect foreign key constraints
            # Sync organizations first
            sync_table_supabase(local_db, Organization)

            # Sync outlets (needed for users)
            sync_table_supabase(local_db, Outlet)

            # Sync users (depends on outlets)
            sync_table_supabase(local_db, User)

            # Sync licenses
            sync_table_supabase(local_db, License)

            # Sync categories and units (needed for products)
            sync_table_supabase(local_db, Category)
            sync_table_supabase(local_db, Unit)

            # Sync suppliers (needed for purchases)
            sync_table_supabase(local_db, Supplier)

            # Sync Customers (needed for purchases)
            sync_table_supabase(local_db, Customer)

            # Sync products
            sync_table_supabase(local_db, Product)

            # Sync purchases and items
            sync_table_supabase(local_db, Purchase)
            sync_table_supabase(local_db, PurchaseItem)

            # Sync sales and items
            sync_table_supabase(local_db, Sale)
            sync_table_supabase(local_db, SaleItem)

            # Sync payments
            sync_table_supabase(local_db, Payment)

            # Sync other tables
            sync_table_supabase(local_db, UserActivityLog)
            sync_table_supabase(local_db, PrinterSettings)
            sync_table_supabase(local_db, InvoiceTemplate)
            sync_table_supabase(local_db, SalePayment)
            sync_table_supabase(local_db, CashierShift)
            sync_table_supabase(local_db, CashierStation)

        logger.info("Sync completed successfully.")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
    finally:
        local_db.close()

def sync_table_sqlalchemy(local_db: Session, central_db: Session, model):
    """Sync a single table from local to central PostgreSQL DB using upsert logic."""
    try:
        local_records = local_db.query(model).all()
        for record in local_records:
            try:
                if model.__name__ == "Organization":
                    # For organizations, use email as unique key instead of ID
                    existing = central_db.query(model).filter(model.email == record.email).first()
                    if existing:
                        # Update existing record
                        for attr in model.__table__.columns.keys():
                            if attr != 'id':  # Don't update ID
                                setattr(existing, attr, getattr(record, attr))
                    else:
                        # Insert new record
                        central_db.add(record)
                else:
                    # Try to add or update the record in central DB
                    central_db.merge(record)
            except IntegrityError:
                central_db.rollback()
                logger.warning(f"Integrity error for {model.__name__} id {record.id}, skipping.")
    except Exception as e:
        logger.error(f"Error syncing {model.__name__}: {e}")

def sync_table_supabase(local_db: Session, model):
    """Sync a single table from local to Supabase using upsert logic."""
    try:
        local_records = local_db.query(model).all()
        table_name = model.__tablename__
        for record in local_records:
            try:
                # Convert SQLAlchemy model to dict, handling datetime serialization
                record_dict = {}
                for column in record.__table__.columns:
                    value = getattr(record, column.name)
                    if hasattr(value, 'isoformat'):  # datetime objects
                        record_dict[column.name] = value.isoformat()
                    else:
                        record_dict[column.name] = value

                if model.__name__ == "Organization":
                    # For organizations, use email as unique key for upsert
                    # Supabase upsert will handle insert/update based on email
                    supabase.table(table_name).upsert(record_dict, on_conflict=['email']).execute()
                else:
                    # Use upsert to insert or update
                    supabase.table(table_name).upsert(record_dict).execute()
            except Exception as e:
                logger.warning(f"Error syncing {model.__name__} id {record.id} to Supabase: {e}")
    except Exception as e:
        logger.error(f"Error syncing {model.__name__} to Supabase: {e}")
