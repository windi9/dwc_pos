# app/schemas/product.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Impor skema UOM yang baru kita buat
from app.schemas.uom import UOMInDB # Menggunakan UOMInDB untuk representasi nested UOM

# Shared properties
class ProductBase(BaseModel):
    company_id: int = Field(..., description="ID of the company this product belongs to")
    name: str = Field(..., max_length=255, description="Name of the product")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    sku: str = Field(..., max_length=50, description="Stock Keeping Unit (Unique identifier)")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode (if applicable)")
    stock_uom_id: int = Field(..., description="ID of the primary Unit of Measure for stock management")
    base_price: float = Field(..., gt=0, description="Base selling price of the product (must be greater than 0)")
    is_active: bool = Field(True, description="Is the product currently active and available?")
    image_url: Optional[str] = Field(None, description="URL to the product image")

# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass

# Properties to receive via API on update
class ProductUpdate(ProductBase):
    company_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=100)
    stock_uom_id: Optional[int] = None
    base_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = None

# Properties to return via API (read from DB) - includes full UOM details
class ProductInDB(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Nested Pydantic model for UOM relationship
    # SQLAlchemy ORM will populate this when you load the product with its stock_uom
    stock_uom: UOMInDB # Ini akan secara otomatis memuat detail UOM terkait

    model_config = {
        "from_attributes": True # Allow Pydantic to read ORM models
    }

# Additional properties to return via API (same as ProductInDB for now)
class Product(ProductInDB):
    pass