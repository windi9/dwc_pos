# app/models/user_role.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship # Pastikan ini diimpor

from app.db.base import Base # Pastikan import path benar

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    # Definisi relasi
    # `back_populates` harus sesuai dengan nama relasi di model terkait
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"