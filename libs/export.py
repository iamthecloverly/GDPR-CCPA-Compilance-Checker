"""Export utilities for compliance scan results."""

import csv
import json
import logging
from io import StringIO
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def export_scan_to_csv(scan_data: Dict[str, Any]) -> str:
    """
    Export scan result to CSV format.
    
    Args:
        scan_data: Scan result dictionary
        
    Returns:
        CSV formatted string
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Compliance Scan Report'])
    writer.writerow([''])
    
    # Metadata
    writer.writerow(['URL', scan_data.get('url', 'N/A')])
    writer.writerow(['Scan Date', scan_data.get('scan_date', 'N/A')])
    writer.writerow(['Overall Score', f"{scan_data.get('overall_score', 0):.1f}%"])
    writer.writerow(['Grade', scan_data.get('grade', 'N/A')])
    writer.writerow(['Status', scan_data.get('status', 'N/A')])
    writer.writerow([''])
    
    # Score breakdown if available
    if 'score_breakdown' in scan_data:
        writer.writerow(['Category', 'Points'])
        for item in scan_data['score_breakdown']:
            writer.writerow([item.get('category', ''), item.get('points', 0)])
        writer.writerow([''])
    
    # Findings
    writer.writerow(['Findings Summary'])
    writer.writerow(['Category', 'Count'])
    findings = scan_data.get('findings', {})
    for category, count in findings.items():
        writer.writerow([category, count])
    writer.writerow([''])
    
    # Details
    if 'details' in scan_data:
        writer.writerow(['Detailed Analysis'])
        for key, value in scan_data['details'].items():
            writer.writerow([key, str(value)])
    
    return output.getvalue()


def export_scan_to_json(scan_data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Export scan result to JSON format.
    
    Args:
        scan_data: Scan result dictionary
        pretty: Whether to format JSON with indentation
        
    Returns:
        JSON formatted string
    """
    # Add export timestamp
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "scan_data": scan_data
    }
    
    indent = 2 if pretty else None
    return json.dumps(export_data, indent=indent, default=str)


def export_batch_results_to_csv(results: List[Dict[str, Any]]) -> str:
    """
    Export batch scan results to CSV format.
    
    Args:
        results: List of scan result dictionaries
        
    Returns:
        CSV formatted string
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['URL', 'Score', 'Grade', 'Status', 'Scan Date', 'GDPR', 'CCPA'])
    
    # Data rows
    for scan in results:
        writer.writerow([
            scan.get('url', ''),
            f"{scan.get('overall_score', 0):.1f}%",
            scan.get('grade', ''),
            scan.get('status', ''),
            scan.get('scan_date', ''),
            scan.get('findings', {}).get('GDPR Issues', 0),
            scan.get('findings', {}).get('CCPA Issues', 0)
        ])
    
    return output.getvalue()


def export_batch_results_to_json(results: List[Dict[str, Any]], pretty: bool = True) -> str:
    """
    Export batch scan results to JSON format.
    
    Args:
        results: List of scan result dictionaries
        pretty: Whether to format JSON with indentation
        
    Returns:
        JSON formatted string
    """
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "batch_size": len(results),
        "results": results
    }
    
    indent = 2 if pretty else None
    return json.dumps(export_data, indent=indent, default=str)


def generate_csv_filename(url: str = None) -> str:
    """
    Generate filename for CSV export.
    
    Args:
        url: Website URL to include in filename
        
    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if url:
        domain = url.replace("https://", "").replace("http://", "").replace("/", "_")[:20]
        return f"compliance_scan_{domain}_{timestamp}.csv"
    return f"compliance_scan_{timestamp}.csv"


def generate_json_filename(url: str = None) -> str:
    """
    Generate filename for JSON export.
    
    Args:
        url: Website URL to include in filename
        
    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if url:
        domain = url.replace("https://", "").replace("http://", "").replace("/", "_")[:20]
        return f"compliance_scan_{domain}_{timestamp}.json"
    return f"compliance_scan_{timestamp}.json"


def validate_export_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate data before export.
    
    Args:
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "No data to export"
    
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    required_fields = ['url', 'overall_score', 'grade']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, ""
