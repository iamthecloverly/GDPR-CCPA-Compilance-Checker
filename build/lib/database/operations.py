from database.db import get_db
from database.models import ComplianceScan
from datetime import datetime, timedelta
from typing import List, Optional


def save_scan_result(results: dict) -> int:
    with get_db() as db:
        summary = results.get('compliance_summary', {})
        category_scores = summary.get('category_scores', {})
        tracking = results.get('tracking_scripts', {})
        policy_analysis = results.get('policy_analysis', {})
        
        scan = ComplianceScan(
            url=results.get('url', ''),
            scan_date=datetime.utcnow(),
            overall_score=summary.get('weighted_score', 0),
            grade=summary.get('grade', 'F'),
            status=summary.get('status', 'Unknown'),
            cookie_consent_score=category_scores.get('cookie_consent', 0),
            privacy_policy_score=category_scores.get('privacy_policy', 0),
            tracker_score=category_scores.get('trackers', 0),
            contact_info_score=category_scores.get('contact_info', 0),
            cookie_banner_detected=results.get('cookie_banner', {}).get('detected', False),
            privacy_policy_found=results.get('privacy_policy', {}).get('found', False),
            total_trackers=tracking.get('total_trackers', 0),
            tracker_names=tracking.get('tracker_names', []),
            gdpr_compliant=policy_analysis.get('gdpr_compliant') if not policy_analysis.get('error') else None,
            ccpa_compliant=policy_analysis.get('ccpa_compliant') if not policy_analysis.get('error') else None,
            full_results=results
        )
        
        db.add(scan)
        db.flush()
        return scan.id


def get_scan_history(url: str, limit: int = 10) -> List[ComplianceScan]:
    with get_db() as db:
        scans = db.query(ComplianceScan).filter(
            ComplianceScan.url == url
        ).order_by(
            ComplianceScan.scan_date.desc()
        ).limit(limit).all()
        return [scan.to_dict() for scan in scans]


def get_recent_scans(days: int = 30, limit: int = 50) -> List[ComplianceScan]:
    with get_db() as db:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        scans = db.query(ComplianceScan).filter(
            ComplianceScan.scan_date >= cutoff_date
        ).order_by(
            ComplianceScan.scan_date.desc()
        ).limit(limit).all()
        return [scan.to_dict() for scan in scans]


def get_all_scanned_urls() -> List[str]:
    with get_db() as db:
        urls = db.query(ComplianceScan.url).distinct().all()
        return [url[0] for url in urls]


def get_score_trend(url: str, limit: int = 10) -> dict:
    scans = get_scan_history(url, limit)
    if not scans:
        return {'dates': [], 'scores': [], 'grades': []}
    
    scans_reversed = list(reversed(scans))
    
    return {
        'dates': [scan['scan_date'] for scan in scans_reversed],
        'scores': [scan['overall_score'] for scan in scans_reversed],
        'grades': [scan['grade'] for scan in scans_reversed],
        'cookie_scores': [scan['cookie_consent_score'] for scan in scans_reversed],
        'privacy_scores': [scan['privacy_policy_score'] for scan in scans_reversed],
        'tracker_scores': [scan['tracker_score'] for scan in scans_reversed]
    }
