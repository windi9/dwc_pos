# app/models/outlet.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Menggunakan Boolean untuk is_active
    is_active = Column(Boolean, default=True, nullable=False)
    # Kolom untuk soft delete
    deleted_at = Column(DateTime, nullable=True) 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="outlets")
    users = relationship("User", back_populates="outlet")
    
    def __repr__(self):
        return f"<Outlet(id={self.id}, name='{self.name}', company_id={self.company_id}, is_active={self.is_active})>"