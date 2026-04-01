"""Report model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone
import uuid, random

class Report(Base):
    __tablename__ = "reports"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id    = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"))
    prediction_id = Column(String(36), ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True)
    report_code   = Column(String(30), unique=True)
    title         = Column(String(200))
    summary       = Column(Text, nullable=True)
    pdf_url       = Column(String(500), nullable=True)
    is_reviewed   = Column(Boolean, default=False)
    reviewed_by   = Column(String(200), nullable=True)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    patient    = relationship("Patient", back_populates="reports")
    prediction = relationship("Prediction", back_populates="report")
    @staticmethod
    def generate_code(): return f"RPT-{datetime.now().year}-{random.randint(10000,99999)}"
