from database.db import get_db
from database.models import ComplianceScan
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

def save_scan_result(url, results, ai_analysis=None):
    """Save a compliance scan result to the database"""
    with get_db() as db:
        if db is None:
            return None
        
        try:
            scan = ComplianceScan(
                url=url,
                score=results.get("score", 0.0),
                grade=results.get("grade", "F"),
                status=results.get("status", "Unknown"),
                cookie_consent=results.get("cookie_consent", "Not Found"),
                privacy_policy=results.get("privacy_policy", "Not Found"),
                contact_info=results.get("contact_info", "Not Found"),
                trackers=str(results.get("trackers", [])),
                ai_analysis=ai_analysis,
                scan_date=datetime.utcnow()
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)
            return scan.id
        except Exception as e:
            db.rollback()
            raise e

def get_scan_history(url, limit=10):
    """Get scan history for a specific URL"""
    with get_db() as db:
        if db is None:
            return []
        
        try:
            scans = db.query(ComplianceScan).filter(
                ComplianceScan.url == url
            ).order_by(
                desc(ComplianceScan.scan_date)
            ).limit(limit).all()
            
            # Convert to dictionaries to detach from session
            result = []
            for scan in scans:
                result.append({
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'cookie_consent': scan.cookie_consent,
                    'privacy_policy': scan.privacy_policy,
                    'contact_info': scan.contact_info,
                    'trackers': scan.trackers,
                    'scan_date': scan.scan_date,
                    'ai_analysis': scan.ai_analysis
                })
            
            return result
        except Exception as e:
            return []

def get_score_trend(url):
    """Get compliance score trend for a URL"""
    with get_db() as db:
        if db is None:
            return []
        
        try:
            scans = db.query(ComplianceScan).filter(
                ComplianceScan.url == url
            ).order_by(
                ComplianceScan.scan_date.asc()
            ).all()
            
            # Convert to tuples immediately while session is active
            return [(scan.scan_date, scan.score) for scan in scans]
        except Exception as e:
            return []

def get_all_scanned_urls():
    """Get all unique URLs that have been scanned"""
    with get_db() as db:
        if db is None:
            return []
        
        try:
            urls = db.query(ComplianceScan.url).distinct().all()
            return [url[0] for url in urls]
        except Exception as e:
            return []

def get_latest_scan(url):
    """Get the most recent scan for a URL"""
    with get_db() as db:
        if db is None:
            return None
        
        try:
            scan = db.query(ComplianceScan).filter(
                ComplianceScan.url == url
            ).order_by(
                desc(ComplianceScan.scan_date)
            ).first()
            
            if scan:
                # Convert to dictionary to detach from session
                return {
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'cookie_consent': scan.cookie_consent,
                    'privacy_policy': scan.privacy_policy,
                    'contact_info': scan.contact_info,
                    'trackers': scan.trackers,
                    'scan_date': scan.scan_date,
                    'ai_analysis': scan.ai_analysis
                }
            
            return None
        except Exception as e:
            return None
