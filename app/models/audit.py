from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
