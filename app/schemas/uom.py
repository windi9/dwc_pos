# app/schemas/uom.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Shared properties
class UOMBase(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the Unit of Measure")
    symbol: str = Field(..., max_length=10, description="Symbol for the Unit of Measure (e.g., 'kg', 'pcs')")
    is_active: bool = Field(True, description="Is the UOM active?")

# Properties to receive via API on creation
class UOMCreate(UOMBase):
    pass

# Properties to receive via API on update
class UOMUpdate(UOMBase):
    name: Optional[str] = Field(None, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None

# Properties to return via API (read from DB)
class UOMInDB(UOMBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True # Allow Pydantic to read ORM models
    }

# Additional properties to return via API
class UOM(UOMInDB):
    pass