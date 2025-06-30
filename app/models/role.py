# app/models/role.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # Pastikan ini diimpor

from app.db.connection import Base # Pastikan import path benar

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # Gunakan string nama kelas untuk referensi forward declaration
    # Pastikan 'UserRole' dan 'RolePermission' adalah nama kelas yang benar
    users = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"