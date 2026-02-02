"""
Database Operations Module

This module provides CRUD (Create, Read, Update, Delete) operations for managing
compliance scan records in the database. It handles session management and data
serialization for safe detachment from SQLAlchemy sessions.

Functions:
    save_scan_result: Store a compliance scan result
    get_scan_history: Retrieve historical scans for a URL
    get_score_trend: Get compliance score trends over time
    get_all_scanned_urls: Retrieve all unique scanned URLs
    get_latest_scan: Get the most recent scan for a URL

Features:
    - Automatic session management with context managers
    - Proper error handling and logging
    - Data detachment to prevent lazy-loading issues
    - Transaction management (commit/rollback)

Example:
    >>> scan_id = save_scan_result(url, results, ai_analysis)
    >>> history = get_scan_history(url, limit=10)
    >>> trend = get_score_trend(url)
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

from database.db import get_db
from database.models import ComplianceScan
from exceptions import DatabaseError

logger = logging.getLogger(__name__)


def save_scan_result(
    url: str,
    results: Dict[str, Any],
    ai_analysis: Optional[str] = None
) -> Optional[int]:
    """
    Save a compliance scan result to the database.
    
    Args:
        url: Website URL
        results: Scan results dictionary
        ai_analysis: Optional AI-generated analysis
        
    Returns:
        Scan ID if successful, None otherwise
        
    Raises:
        DatabaseError: If database operation fails
    """
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
    """
    Get scan history for a specific URL.
    
    Args:
        url: Website URL
        limit: Maximum number of results to return
        
    Returns:
        List of scan result dictionaries
    """
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
