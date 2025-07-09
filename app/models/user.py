# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True) 

    # --- TAMBAHKAN DUA BARIS INI ---
    outlet_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("outlets.id"), nullable=True)
    # -------------------------------

    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Definisi relasi
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="users")
    user_roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user")

    # --- TAMBAHKAN RELASI INI ---
    outlet: Mapped[Optional["Outlet"]] = relationship("Outlet", back_populates="users")
    # -----------------------------

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"