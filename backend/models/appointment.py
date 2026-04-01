"""Appointment model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone
import uuid, random, enum

class AppointmentStatus(str, enum.Enum):
    PENDING="pending"; CONFIRMED="confirmed"; CANCELLED="cancelled"; COMPLETED="completed"
class AppointmentType(str, enum.Enum):
    IN_PERSON="in_person"; TELEMEDICINE="telemedicine"; SECOND_OPINION="second_opinion"
class SpecialistType(str, enum.Enum):
    ENDOCRINOLOGIST="endocrinologist"; CARDIOLOGIST="cardiologist"
    NEPHROLOGIST="nephrologist"; GP="general_practitioner"

class Appointment(Base):
    __tablename__ = "appointments"
    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id          = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    appointment_code = Column(String(20), unique=True)
    specialist_type  = Column(SAEnum(SpecialistType))
    appointment_type = Column(SAEnum(AppointmentType))
    status           = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.CONFIRMED)
    date             = Column(Date, nullable=False)
    time_slot        = Column(String(20))
    doctor_name      = Column(String(200), nullable=True)
    notes            = Column(Text, nullable=True)
    report_ref       = Column(String(30), nullable=True)
    created_at       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="appointments")
    @staticmethod
    def generate_code(): return f"APT-{random.randint(10000,99999)}"
