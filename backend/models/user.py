"""User model"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone
import uuid, enum

class UserRole(str, enum.Enum):
    PATIENT="patient"; DOCTOR="doctor"; ADMIN="admin"

class User(Base):
    __tablename__ = "users"
    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name      = Column(String(100), nullable=False)
    last_name       = Column(String(100), nullable=False)
    role            = Column(SAEnum(UserRole), default=UserRole.PATIENT)
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login      = Column(DateTime(timezone=True), nullable=True)
    patient         = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    appointments    = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"
