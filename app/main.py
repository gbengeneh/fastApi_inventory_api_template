from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from . import models
from .routers import users, outlets, products, suppliers, sales, auth, settings, cashier_shifts, purchases, payments, organizations, licenses, customers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .sync import sync_data
import logging

app = FastAPI(title="Inventory POS System")

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

# Create tables in central DB if online
from .database import central_engine, is_online
try:
    if is_online():
        Base.metadata.create_all(bind=central_engine)
        logging.info("Central database tables created or verified.")
    else:
        logging.info("Offline: Central database tables not created.")
except Exception as e:
    logging.warning(f"Failed to initialize central database: {e}")

# Scheduler for periodic sync
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Schedule sync every 30 minutes
    scheduler.add_job(sync_data, trigger=IntervalTrigger(minutes=30), id="sync_job")
    scheduler.start()
    logging.info("Scheduler started: Sync job scheduled every 30 minutes.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logging.info("Scheduler shut down.")

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
