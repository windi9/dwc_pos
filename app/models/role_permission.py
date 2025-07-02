# app/models/role_permission.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship # Pastikan ini diimpor

from app.db.base import Base # Pastikan import path benar

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

    # Definisi relasi
    # `back_populates` harus sesuai dengan nama relasi di model terkait
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"