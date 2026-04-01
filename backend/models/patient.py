"""Patient model"""
from sqlalchemy import Column, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime
import uuid, random

class Patient(Base):
    __tablename__ = "patients"
    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id         = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    patient_code    = Column(String(25), unique=True, index=True)
    date_of_birth   = Column(Date, nullable=True)
    sex             = Column(String(10), nullable=True)
    blood_group     = Column(String(5), nullable=True)
    phone           = Column(String(30), nullable=True)
    address         = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies       = Column(Text, nullable=True)
    medications     = Column(Text, nullable=True)
    latest_glucose  = Column(Float, nullable=True)
    latest_bmi      = Column(Float, nullable=True)
    latest_bp_sys   = Column(Float, nullable=True)
    latest_bp_dia   = Column(Float, nullable=True)
    latest_cholesterol = Column(Float, nullable=True)
    latest_insulin  = Column(Float, nullable=True)
    user        = relationship("User", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    reports     = relationship("Report", back_populates="patient", cascade="all, delete-orphan")
    @staticmethod
    def generate_code(): return f"LL-{datetime.now().year}-{random.randint(10000,99999)}"
