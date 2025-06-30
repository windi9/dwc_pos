# dwc_pos/app/db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings # Import settings dari config.py

# SQLAlchemy Engine setup
# DATABASE_URL is for synchronous operations (e.g., Alembic migrations, or sync endpoints)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal class to create a new session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models
Base = declarative_base()

# Dependency to get a database session for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()