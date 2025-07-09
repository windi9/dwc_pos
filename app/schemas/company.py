# app/schemas/company.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    pass # Tidak ada tambahan untuk create

class CompanyUpdate(CompanyBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100) # Jadikan name opsional saat update

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True