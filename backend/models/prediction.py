"""Prediction model"""
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone
import uuid, enum

class DiseaseType(str, enum.Enum):
    DIABETES="diabetes"; HEART="heart_disease"; KIDNEY="kidney_stones"

class RiskLevel(str, enum.Enum):
    LOW="low"; MODERATE="moderate"; HIGH="high"

class Prediction(Base):
    __tablename__ = "predictions"
    id                 = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id         = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    disease_type       = Column(SAEnum(DiseaseType))
    risk_level         = Column(SAEnum(RiskLevel))
    risk_score         = Column(Float)
    confidence         = Column(Float)
    model_name         = Column(String(100))
    model_version      = Column(String(10), default="2.0")
    input_features     = Column(JSON)
    feature_importance = Column(JSON, nullable=True)
    findings           = Column(JSON, nullable=True)
    risk_factors       = Column(JSON, nullable=True)
    recommendations    = Column(JSON, nullable=True)
    doctor_notes       = Column(Text, nullable=True)
    created_at         = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    patient = relationship("Patient", back_populates="predictions")
    report  = relationship("Report", back_populates="prediction", uselist=False)
