from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database.db import Base

class ComplianceScan(Base):
    """Model for storing compliance scan results"""
    __tablename__ = "compliance_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), index=True, nullable=False)
    score = Column(Float, nullable=False)
    grade = Column(String(2), nullable=False)
    status = Column(String(50), nullable=False)
    cookie_consent = Column(String(200))
    privacy_policy = Column(String(200))
    contact_info = Column(String(200))
    trackers = Column(Text)
    scan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    ai_analysis = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ComplianceScan(url={self.url}, score={self.score}, date={self.scan_date})>"
