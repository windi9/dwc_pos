# app/models/uom.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship # Tambahkan relationship di sini
from typing import List # Tambahkan ini jika belum ada
from app.db.base import Base

class UOM(Base):
    __tablename__ = "uoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Tambahkan relationship ini
    products: Mapped[List["Product"]] = relationship("Product", back_populates="stock_uom")


    def __repr__(self):
        return f"<UOM(name='{self.name}', symbol='{self.symbol}')>"