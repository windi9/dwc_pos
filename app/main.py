# dwc_pos/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import engine, Base # Import Base dan engine
from app.core.config import settings # Import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This function will run when the app starts and shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    logger.info("Ensuring database tables exist (if not, creating them for initial setup/testing)...")
    
    # Import app.db.base to ensure all models are registered with Base.metadata
    # This is crucial for Base.metadata.create_all to find all your models.
    # In production, you'll primarily rely on Alembic migrations.
    import app.db.base # This import makes sure all models defined in app/models are known to Base.metadata
    
    # Optional: Uncomment Base.metadata.create_all for initial table creation during development
    # If you prefer to use Alembic from the start, keep this commented.
    # Base.metadata.create_all(bind=engine) 
    
    logger.info("Database table check/creation completed (or skipped if using Alembic).")
    logger.info("Application ready to serve requests.")
    yield
    logger.info("Application shutting down.")
    logger.info("Application shutdown complete.")

# Initialize FastAPI app with settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Professional Backend API for a DWC Point of Sale System with multiple interfaces.",
    lifespan=lifespan # Apply the lifespan context manager
)

# --- Include main API router (akan dibuat di langkah selanjutnya) ---
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")

# Root endpoint for health check
@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} API!"}