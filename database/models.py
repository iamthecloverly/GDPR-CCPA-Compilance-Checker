from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Text
from datetime import datetime
from database.db import Base


class ComplianceScan(Base):
    __tablename__ = "compliance_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    scan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    overall_score = Column(Float, nullable=False)
    grade = Column(String(2), nullable=False)
    status = Column(String(50), nullable=False)
    
    cookie_consent_score = Column(Float, nullable=False)
    privacy_policy_score = Column(Float, nullable=False)
    tracker_score = Column(Float, nullable=False)
    contact_info_score = Column(Float, nullable=False)
    
    cookie_banner_detected = Column(Boolean, nullable=False)
    privacy_policy_found = Column(Boolean, nullable=False)
    total_trackers = Column(Integer, nullable=False)
    tracker_names = Column(JSON, nullable=True)
    
    gdpr_compliant = Column(Boolean, nullable=True)
    ccpa_compliant = Column(Boolean, nullable=True)
    
    full_results = Column(JSON, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'scan_date': self.scan_date.isoformat() if self.scan_date else None,
            'overall_score': self.overall_score,
            'grade': self.grade,
            'status': self.status,
            'cookie_consent_score': self.cookie_consent_score,
            'privacy_policy_score': self.privacy_policy_score,
            'tracker_score': self.tracker_score,
            'contact_info_score': self.contact_info_score,
            'cookie_banner_detected': self.cookie_banner_detected,
            'privacy_policy_found': self.privacy_policy_found,
            'total_trackers': self.total_trackers,
            'tracker_names': self.tracker_names,
            'gdpr_compliant': self.gdpr_compliant,
            'ccpa_compliant': self.ccpa_compliant
        }
