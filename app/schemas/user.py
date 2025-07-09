# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Untuk nested response dari Company
from app.schemas.company import Company as CompanySchema # Asumsikan CompanySchema sudah ada

# Schema dasar untuk membuat User
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8) # Password raw
    full_name: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = None # Opsional, bisa null untuk superadmin
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Schema untuk update User (semua opsional)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Schema untuk respons User (output dari API)
class User(BaseModel):
    id: int
    company_id: Optional[int] = None
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Untuk menampilkan detail Company secara nested
    # Gunakan CompanySchema yang sudah ada
    company: Optional[CompanySchema] = None # Relasi ke Company

    class ConfigDict: # Gunakan ConfigDict untuk Pydantic v2+
        from_attributes = True # Menggantikan orm_mode = True