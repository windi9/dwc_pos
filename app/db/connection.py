# app/db/connection.py

# Ganti 'create_engine' dengan 'create_async_engine'
# Ganti 'sessionmaker' dengan 'async_sessionmaker'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base # Ini tetap sama
from app.core.config import settings

# Define the database URL based on your settings
# Pastikan ini menggunakan 'postgresql+asyncpg://'
SQLALCHEMY_DATABASE_URL = settings.DATABASE_ASYNC_URL

# Create the SQLAlchemy ASYNC engine
# Tambahkan 'future=True' untuk kompatibilitas SQLAlchemy 2.0
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True, # Biarkan ini untuk melihat query SQL di console (opsional)
    future=True # Penting untuk mode 2.0
)

# Create an AsyncSessionLocal class
# Ganti SessionLocal dengan AsyncSessionLocal
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession # Penting: Tentukan class_ sebagai AsyncSession
)

# Base class for declarative models (ini tetap sama)
Base = declarative_base()

# --- UBAH FUNGSI get_db MENJADI ASYNC GENERATOR ---
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
# --- END FUNGSI get_db ---

# --- BAGIAN IMPOR SEMUA MODEL (biarkan ini sama seperti sebelumnya, ini sudah benar) ---
import app.models.user
import app.models.role
import app.models.permission
import app.models.user_role
import app.models.role_permission
# Tambahkan semua model Anda yang lain di sini