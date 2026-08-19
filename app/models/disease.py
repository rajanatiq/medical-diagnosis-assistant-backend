from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.session import Base

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    specialty = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    precaution_1 = Column(String(255), nullable=True)
    precaution_2 = Column(String(255), nullable=True)
    precaution_3 = Column(String(255), nullable=True)
    precaution_4 = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
