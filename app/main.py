# D:\pythonproject\dwc_pos\app\main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.connection import engine, Base
from app.core.config import settings
import logging

# Import the main API router for v1
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define lifespan context for application startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: Initialize database (if not using Alembic for initial setup)
    logging.info("Application startup...")
    # Optional: If you want to create tables automatically on startup (less common with Alembic)
    # Base.metadata.create_all(bind=engine)
    yield
    # Shutdown event: Perform cleanup (e.g., close database connections if not handled by SQLAlchemy itself)
    logging.info("Application shutdown.")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    # Set the OpenAPI URL for Swagger UI and ReDoc
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan # Include lifespan context
)

# Configure CORS middleware
# These origins allow requests from localhost.
# You might need to add other frontend origins here (e.g., "http://localhost:3000" for a React app)
origins = [
    "http://localhost",
    "http://localhost:8000", # The port Uvicorn is running on
    # You can add more origins as needed for your frontend applications, e.g.:
    # "http://localhost:3000",
    # "http://192.168.1.100:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of origins that are allowed to make requests
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all headers in cross-origin requests
)

# Include the main API router for version 1
# All routes defined in api_router will be prefixed with /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# Define a root endpoint for the API
# This is optional but good for basic health checks or a welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to DWC POS API v1! Access the API documentation at /docs."}