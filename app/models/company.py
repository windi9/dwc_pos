# app/models/company.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    
    # Menggunakan Boolean untuk is_active
    is_active = Column(Boolean, default=True, nullable=False) 
    # Kolom untuk soft delete
    deleted_at = Column(DateTime, nullable=True) 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    outlets = relationship("Outlet", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', is_active={self.is_active})>"