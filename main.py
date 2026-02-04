from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal, central_engine, POSTGRESQL_DATABASE_URL, get_db_status
from app import models
from app.routers import users, outlets, products, suppliers, sales, auth, settings, cashier_shifts, purchases, payments, organizations, licenses, customers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.sync import sync_data
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
import logging

def run_central_migrations():
    """Run Alembic migrations on the central database if PostgreSQL is available and pending."""
    status = get_db_status()
    if status != "postgresql":
        logging.info(f"Central database not PostgreSQL ({status}): Skipping migrations.")
        return

    try:
        # Create custom Alembic config for central DB
        config = Config()
        config.set_main_option("script_location", "alembic")
        # Escape % to %% to avoid interpolation issues
        escaped_url = POSTGRESQL_DATABASE_URL.replace("%", "%%")
        config.set_main_option("sqlalchemy.url", escaped_url)

        # Get script directory
        script = ScriptDirectory.from_config(config)

        # Get current revision from central DB
        with central_engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        head_rev = script.get_current_head()

        if current_rev != head_rev:
            logging.info("Pending migrations found on central database. Running upgrade...")
            command.upgrade(config, "head")
            logging.info("Central database migrations completed successfully.")
        else:
            logging.info("Central database is up to date.")

    except Exception as e:
        logging.error(f"Failed to run central database migrations: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    run_central_migrations()
    scheduler.add_job(sync_data, trigger=IntervalTrigger(minutes=30), id="sync_job")
    scheduler.start()
    logging.info("Scheduler started: Sync job scheduled every 30 minutes.")
    yield
    # Shutdown logic
    scheduler.shutdown()
    logging.info("Scheduler shut down.")

app = FastAPI(title="Inventory POS System", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Create tables in central DB if PostgreSQL is available
status = get_db_status()
try:
    if status == "postgresql":
        Base.metadata.create_all(bind=central_engine)
        logging.info("Central database tables created or verified.")
    else:
        logging.info(f"Central database not PostgreSQL ({status}): Tables not created.")
except Exception as e:
    logging.warning(f"Failed to initialize central database: {e}")

# Scheduler for periodic sync
scheduler = AsyncIOScheduler()

@app.get("/")
def root():
    return {"message": "Inventory POS backend running!"}

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(outlets.router, prefix="/api", tags=["outlets"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])
app.include_router(sales.router, prefix="/api", tags=["sales"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(cashier_shifts.router, prefix="/api", tags=["cashier-shifts"])
app.include_router(purchases.router, prefix="/api", tags=["purchases"])
app.include_router(payments.router, prefix="/api", tags=["payments"])
app.include_router(organizations.router, prefix="/api", tags=["organizations"])
app.include_router(licenses.router, prefix="/api", tags=["licenses"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
