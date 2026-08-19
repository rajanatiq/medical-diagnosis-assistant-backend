from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.session import Base

class HealthcareProvider(Base):
    __tablename__ = "healthcare_providers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    facility_type = Column(String(100), default="Clinic")
    specialty = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), default="Islamabad")
    phone = Column(String(50), nullable=True)
    emergency_capable = Column(Boolean, default=False, index=True)
    rating = Column(Float, default=4.5)
    hours = Column(String(100), default="24/7 Open")
