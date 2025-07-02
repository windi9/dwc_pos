# app/models/permission.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # Pastikan ini diimpor

from app.db.base import Base # Pastikan import path benar

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relasi ke RolePermission
    # Pastikan `back_populates` sesuai dengan nama relasi di RolePermission
    # dan 'RolePermission' adalah nama kelas yang benar
    roles = relationship("RolePermission", back_populates="permission")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"