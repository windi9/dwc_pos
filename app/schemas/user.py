# dwc_pos/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# For user creation/update by admin
class UserCreate(BaseModel):
    username: str = Field(..., example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="secure_password") # Admin sets initial password
    phone_number: Optional[str] = Field(None, example="+628123456789")
    full_name: Optional[str] = Field(None, example="John Doe")
    is_active: Optional[bool] = True
    email_verified: Optional[bool] = False # Admin can manually verify
    pin: Optional[str] = Field(None, description="6-digit PIN for POS login, will be hashed if provided")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, example="john_doe_new")
    email: Optional[EmailStr] = Field(None, example="john.new@example.com")
    password: Optional[str] = Field(None, example="new_secure_password")
    phone_number: Optional[str] = Field(None, example="+6281234567890")
    full_name: Optional[str] = Field(None, example="John Doe Updated")
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None
    pin: Optional[str] = Field(None, description="6-digit PIN for POS login, will be hashed if provided")

# For displaying user information (response model)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    # No password or PIN in response for security

    class Config:
        from_attributes = True # Pydantic v2