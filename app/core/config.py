# dwc_pos/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os

class Settings(BaseSettings):
    # Base settings for the application
    PROJECT_NAME: str = "DWC POS Backend" # Nama proyek yang sudah diperbarui
    PROJECT_VERSION: str = "0.1.0"

    # Database settings
    DATABASE_URL: str
    DATABASE_ASYNC_URL: str # Untuk dukungan asyncpg di masa depan

    # Security settings
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # Default 60 menit

    # Pydantic settings configuration to load from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Create an instance of Settings to be used throughout the application
settings = Settings()

# Optional: Create a .env file if it doesn't exist for easier initial setup
# This path assumes .env is in the project root
env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_file_path):
    print(f"Creating an empty .env file at {env_file_path}")
    with open(env_file_path, 'w') as f:
        f.write("# Database Connection String (for SQLAlchemy)\n")
        f.write("DATABASE_URL=\"postgresql://user:password@host:port/dbname\"\n")
        f.write("DATABASE_ASYNC_URL=\"postgresql+asyncpg://user:password@host:port/dbname\"\n")
        f.write("\n# JWT Secret Key (Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))')\n")
        f.write("SECRET_KEY=\"your_generated_secret_key_here\"\n")
        f.write("\n# JWT Token Expiration in minutes\n")
        f.write("ACCESS_TOKEN_EXPIRE_MINUTES=60\n")