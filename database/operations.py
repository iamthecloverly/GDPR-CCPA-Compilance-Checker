"""Database CRUD operations for compliance scan records."""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

from database.db import get_db
from database.models import ComplianceScan
from exceptions import DatabaseError

logger = logging.getLogger(__name__)


def save_scan_result(url: str, results: Dict[str, Any], ai_analysis: Optional[str] = None) -> Optional[int]:
    """Save compliance scan result to database."""
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - scan not saved")
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
            logger.info(f"Saved scan result for {url} with ID {scan.id}")
            return scan.id
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save scan result: {e}")
            raise DatabaseError(f"Failed to save scan result: {str(e)}") from e


def get_scan_history(url: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get scan history for a specific URL."""
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty history")
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
            
            logger.info(f"Retrieved {len(result)} scan records for {url}")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve scan history: {e}")
            return []


def get_score_trend(url: str) -> List[Tuple[datetime, float]]:
    """
    Get compliance score trend for a URL.
    
    Args:
        url: Website URL
        
    Returns:
        List of (date, score) tuples in chronological order
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty trend")
            return []
        
        try:
            scans = db.query(ComplianceScan).filter(
                ComplianceScan.url == url
            ).order_by(
                ComplianceScan.scan_date.asc()
            ).all()
            
            # Convert to tuples immediately while session is active
            trend = [(scan.scan_date, scan.score) for scan in scans]
            logger.info(f"Retrieved score trend for {url}: {len(trend)} data points")
            return trend
        except Exception as e:
            logger.error(f"Failed to retrieve score trend: {e}")
            return []


def get_all_scanned_urls() -> List[str]:
    """
    Get all unique URLs that have been scanned.
    
    Returns:
        List of unique URL strings
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty URL list")
            return []
        
        try:
            urls = db.query(ComplianceScan.url).distinct().all()
            result = [url[0] for url in urls]
            logger.info(f"Retrieved {len(result)} unique scanned URLs")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve scanned URLs: {e}")
            return []


def get_latest_scan(url: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent scan for a URL.
    
    Args:
        url: Website URL
        
    Returns:
        Dictionary with scan details or None if not found
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning None")
            return None
        
        try:
            scan = db.query(ComplianceScan).filter(
                ComplianceScan.url == url
            ).order_by(
                desc(ComplianceScan.scan_date)
            ).first()
            
            if scan:
                # Convert to dictionary to detach from session
                result = {
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
                logger.info(f"Retrieved latest scan for {url}")
                return result
            
            logger.info(f"No scans found for {url}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve latest scan: {e}")
            return None

def get_recent_scans(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent scans across all URLs.
    
    Args:
        limit: Maximum number of scans to retrieve
        
    Returns:
        List of scan result dictionaries
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty list")
            return []
        
        try:
            scans = db.query(ComplianceScan).order_by(
                desc(ComplianceScan.scan_date)
            ).limit(limit).all()
            
            result = []
            for scan in scans:
                result.append({
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'scan_date': scan.scan_date,
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve recent scans: {e}")
            return []


def get_all_scans() -> List[Dict[str, Any]]:
    """
    Get all scans from database.
    
    Returns:
        List of all scan result dictionaries
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty list")
            return []
        
        try:
            scans = db.query(ComplianceScan).order_by(
                desc(ComplianceScan.scan_date)
            ).all()
            
            result = []
            for scan in scans:
                result.append({
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'scan_date': scan.scan_date,
                    'findings': {
                        'cookie_consent': scan.cookie_consent,
                        'privacy_policy': scan.privacy_policy,
                        'contact_info': scan.contact_info,
                    },
                    'trackers': scan.trackers,
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve all scans: {e}")
            return []


def get_scan_statistics() -> Dict[str, Any]:
    """
    Get overall scan statistics.
    
    Returns:
        Dictionary with statistics
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty stats")
            return {
                'total_scans': 0,
                'avg_score': 0,
                'compliant_count': 0,
                'at_risk_count': 0,
            }
        
        try:
            total = db.query(func.count(ComplianceScan.id)).scalar() or 0
            avg_score = db.query(func.avg(ComplianceScan.score)).scalar() or 0
            compliant = db.query(func.count(ComplianceScan.id)).filter(
                ComplianceScan.score >= 80
            ).scalar() or 0
            at_risk = db.query(func.count(ComplianceScan.id)).filter(
                ComplianceScan.score < 60
            ).scalar() or 0
            
            return {
                'total_scans': total,
                'avg_score': float(avg_score),
                'compliant_count': compliant,
                'at_risk_count': at_risk,
            }
        except Exception as e:
            logger.error(f"Failed to retrieve statistics: {e}")
            return {
                'total_scans': 0,
                'avg_score': 0,
                'compliant_count': 0,
                'at_risk_count': 0,
            }


def get_scan_by_url(url: str) -> List[Dict[str, Any]]:
    """
    Get all scans for a specific URL.
    
    Args:
        url: Website URL (can be partial search)
        
    Returns:
        List of scan result dictionaries
    """
    with get_db() as db:
        if db is None:
            return []
        
        try:
            scans = db.query(ComplianceScan).filter(
                ComplianceScan.url.ilike(f"%{url}%")
            ).order_by(
                desc(ComplianceScan.scan_date)
            ).all()
            
            result = []
            for scan in scans:
                result.append({
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'scan_date': scan.scan_date,
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve scans for {url}: {e}")
            return []


def delete_scan(scan_id: int) -> bool:
    """
    Delete a scan by ID.
    
    Args:
        scan_id: ID of scan to delete
        
    Returns:
        True if successful, False otherwise
    """
    with get_db() as db:
        if db is None:
            return False
        
        try:
            scan = db.query(ComplianceScan).filter(
                ComplianceScan.id == scan_id
            ).first()
            
            if scan:
                db.delete(scan)
                db.commit()
                logger.info(f"Deleted scan {scan_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete scan {scan_id}: {e}")
            return False


def get_scans_by_date_range(start_date, end_date) -> List[Dict[str, Any]]:
    """
    Get scans within a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of scan result dictionaries
    """
    with get_db() as db:
        if db is None:
            return []
        
        try:
            scans = db.query(ComplianceScan).filter(
                ComplianceScan.scan_date >= start_date,
                ComplianceScan.scan_date <= end_date
            ).order_by(
                desc(ComplianceScan.scan_date)
            ).all()
            
            result = []
            for scan in scans:
                result.append({
                    'id': scan.id,
                    'url': scan.url,
                    'score': scan.score,
                    'grade': scan.grade,
                    'status': scan.status,
                    'scan_date': scan.scan_date,
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve scans by date range: {e}")
            return []