# app/models/product.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    sku: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False) # Stock Keeping Unit
    barcode: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True) # Optional barcode

    # Foreign key to UOM for the standard stock unit of this product
    stock_uom_id: Mapped[int] = mapped_column(Integer, ForeignKey("uoms.id"), nullable=False)

    base_price: Mapped[float] = mapped_column(Float, nullable=False) # Base selling price of the product
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="products")
    stock_uom: Mapped["UOM"] = relationship("UOM", back_populates="products") # Assuming UOM will have 'products' back_populates

    # Unique constraint for name and sku within a company (if needed, otherwise remove company_id from this)
    __table_args__ = (
        UniqueConstraint('name', 'company_id', name='_name_company_uc'),
        UniqueConstraint('sku', 'company_id', name='_sku_company_uc'),
    )


    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}', company_id={self.company_id})>"