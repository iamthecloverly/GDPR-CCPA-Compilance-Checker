"""Database CRUD operations for compliance scan records."""

from typing import Dict, List, Any, Optional, Tuple
import ast
import json
import logging
from datetime import datetime
from sqlalchemy import func, desc

from database.db import get_db
from database.models import ComplianceScan
from exceptions import DatabaseError

logger = logging.getLogger(__name__)

def _parse_trackers(raw: Any) -> list:
    """Safely parse trackers from DB — handles both JSON and legacy Python-repr strings."""
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Legacy rows stored as Python repr: "['google-analytics.com', 'facebook.net']"
        try:
            val = ast.literal_eval(raw)
            return val if isinstance(val, list) else []
        except Exception:
            return []


def _scan_to_dict(scan: ComplianceScan, include_findings: bool = False) -> Dict[str, Any]:
    """Convert a ComplianceScan model instance to a dictionary."""
    d = {
        'id': scan.id,
        'url': scan.url,
        'score': scan.score,
        'grade': scan.grade,
        'status': scan.status,
        'cookie_consent': scan.cookie_consent,
        'privacy_policy': scan.privacy_policy,
        'contact_info': scan.contact_info,
        'trackers': _parse_trackers(scan.trackers),
        'scan_date': scan.scan_date,
        'ai_analysis': scan.ai_analysis,
    }
    if include_findings:
        d['findings'] = {
            'cookie_consent': scan.cookie_consent,
            'privacy_policy': scan.privacy_policy,
            'contact_info': scan.contact_info,
        }
    return d


def _apply_scan_filters(q, url_search, grade_filter, date_cutoff):
    """Apply common scan filters to a SQLAlchemy query and return it."""
    if url_search:
        q = q.filter(ComplianceScan.url.ilike(f"%{url_search}%"))
    if grade_filter:
        q = q.filter(ComplianceScan.grade.in_(grade_filter))
    if date_cutoff:
        q = q.filter(ComplianceScan.scan_date >= date_cutoff)
    return q


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
                trackers=json.dumps(results.get("trackers", [])),
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
            result = [_scan_to_dict(scan) for scan in scans]
            
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
                result = _scan_to_dict(scan)
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
            
            return [_scan_to_dict(scan) for scan in scans]
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
            
            return [_scan_to_dict(scan, include_findings=True) for scan in scans]
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
            
            return [_scan_to_dict(scan) for scan in scans]
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


def delete_scans_by_ids(scan_ids: List[int]) -> int:
    """
    Delete multiple scans by their IDs in a single transaction.

    Args:
        scan_ids: List of scan IDs to delete.

    Returns:
        Number of records actually deleted.
    """
    if not scan_ids:
        return 0
    with get_db() as db:
        if db is None:
            return 0
        try:
            deleted = (
                db.query(ComplianceScan)
                .filter(ComplianceScan.id.in_(scan_ids))
                .delete(synchronize_session=False)
            )
            db.commit()
            logger.info(f"Bulk deleted {deleted} scan(s): ids={scan_ids}")
            return deleted
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to bulk delete scans {scan_ids}: {e}")
            return 0


def get_scan_count(
    url_search: Optional[str] = None,
    grade_filter: Optional[List[str]] = None,
    date_cutoff: Optional[datetime] = None,
) -> int:
    """
    Return the total number of scans matching the given filters.

    Args:
        url_search: Partial URL substring to filter by (case-insensitive).
        grade_filter: List of grade letters to include (e.g. ["A", "B"]).
        date_cutoff: Only count scans on or after this datetime.

    Returns:
        Integer count of matching scans.
    """
    with get_db() as db:
        if db is None:
            return 0
        try:
            q = _apply_scan_filters(
                db.query(func.count(ComplianceScan.id)),
                url_search, grade_filter, date_cutoff,
            )
            return q.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to count scans: {e}")
            return 0


def get_scans_paginated(
    offset: int = 0,
    limit: int = 20,
    url_search: Optional[str] = None,
    grade_filter: Optional[List[str]] = None,
    date_cutoff: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Return a page of scans matching the given filters, newest-first.

    Args:
        offset: Number of records to skip (0-based).
        limit: Maximum records to return.
        url_search: Partial URL substring to filter by (case-insensitive).
        grade_filter: List of grade letters to include (e.g. ["A", "B"]).
        date_cutoff: Only return scans on or after this datetime.

    Returns:
        List of scan result dictionaries.
    """
    with get_db() as db:
        if db is None:
            logger.warning("Database not available - returning empty page")
            return []
        try:
            q = _apply_scan_filters(
                db.query(ComplianceScan).order_by(desc(ComplianceScan.scan_date)),
                url_search, grade_filter, date_cutoff,
            )
            scans = q.offset(offset).limit(limit).all()
            return [_scan_to_dict(scan, include_findings=True) for scan in scans]
        except Exception as e:
            logger.error(f"Failed to retrieve paginated scans: {e}")
            return []


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
            
            return [_scan_to_dict(scan) for scan in scans]
        except Exception as e:
            logger.error(f"Failed to retrieve scans by date range: {e}")
            return []