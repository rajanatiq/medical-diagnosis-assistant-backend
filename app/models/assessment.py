from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    symptoms_json = Column(Text, nullable=False)
    duration_days = Column(Integer, default=1)
    age_band = Column(String(50), nullable=True)
    sex = Column(String(20), nullable=True)
    model_version = Column(String(50), default="v2.0.0")
    predictions_json = Column(Text, nullable=False)
    urgency = Column(String(50), nullable=False, index=True)
    red_flag_triggered = Column(Boolean, default=False)
    red_flag_reason = Column(String(255), nullable=True)
    composite_severity = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="assessments")
