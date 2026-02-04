from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
from supabase import create_client, Client
import os
from urllib.parse import quote_plus

# Local SQLite (always available) - moved to APPDATA to avoid src-tauri conflicts
app_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'InventoryBoss')
os.makedirs(app_data_dir, exist_ok=True)
db_path = os.path.join(app_data_dir, 'inventory.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Remote PostgreSQL / Supabase details
raw_password = "Gbenga12@#12"
encoded_password = quote_plus(raw_password)
POSTGRESQL_DATABASE_URL = f"postgresql+psycopg2://postgres:{encoded_password}@db.bvmgydhrvufwubjecmzm.supabase.co:5432/postgres"
SUPABASE_URL = "https://bvmgydhrvufwubjecmzm.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2bWd5ZGhydnVmd3ViamVjbXptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2NzY3ODYsImV4cCI6MjA3NzI1Mjc4Nn0.o6OxswT6flVsGjM4dr2S-NliqFRW8mOAEx0vDJbhPx0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

central_engine = None  # ⬅️ don’t create yet
CentralSessionLocal = None

def init_central_db():
    """Try to initialize central PostgreSQL if available."""
    global central_engine, CentralSessionLocal
    try:
        test_engine = create_engine(POSTGRESQL_DATABASE_URL, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute("SELECT 1")
        central_engine = test_engine
        CentralSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=central_engine)
        logging.info("✅ Central PostgreSQL connection established.")
        return "postgresql"
    except OperationalError as e:
        # Suppress the warning to avoid cluttering logs during startup
        # logging.warning(f"⚠️ Central DB connection failed: {e}")
        # Try Supabase REST API as fallback
        try:
            supabase.table("organizations").select("*").limit(1).execute()
            logging.info("✅ Supabase client available.")
            return "supabase"
        except Exception as e:
            # Suppress the warning to avoid cluttering logs during startup
            # logging.warning(f"⚠️ Supabase client also failed: {e}")
            return "offline"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_central_db():
    if CentralSessionLocal is None:
        raise RuntimeError("Central DB not initialized or unavailable.")
    db = CentralSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_status():
    """Get the status of the central database connection."""
    return init_central_db()
