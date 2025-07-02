# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base # <--- UBAH IMPOR BASE DARI SINI

class UserAccessType(enum.Enum):
    GLOBAL = "global"
    OUTLET_SPECIFIC = "outlet_specific"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    full_name = Column(String(255), nullable=False)
    pin = Column(String(255), nullable=True) # Untuk login POS
    
    # Menggunakan Boolean untuk is_active
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    # Kolom untuk soft delete
    deleted_at = Column(DateTime, nullable=True) 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # --- Kolom untuk Akses Pengguna Multi-Outlet ---
    access_type = Column(
        SQLEnum(UserAccessType),
        nullable=False,
        default=UserAccessType.OUTLET_SPECIFIC
    )
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=True
    )

    # Relationships
    roles = relationship("UserRole", back_populates="user")
    outlet = relationship("Outlet", back_populates="users")
    # production_orders = relationship("ProductionOrder", back_populates="producer")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', access_type='{self.access_type.value}', outlet_id={self.outlet_id}, is_active={self.is_active})>"