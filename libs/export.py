"""Export utilities for compliance scan results."""

import csv
import json
import logging
from io import StringIO, BytesIO
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

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


def format_full_scan_text(scan_data: Dict[str, Any]) -> str:
    """
    Format scan result as comprehensive text report (for copy feature).
    Combines findings, recommendations, and AI analysis.
    
    Args:
        scan_data: Scan result dictionary
        
    Returns:
        Formatted text report combining all sections
    """
    report = f"""
{'='*70}
GDPR/CCPA COMPLIANCE SCAN REPORT
{'='*70}

URL: {scan_data.get('url', 'N/A')}
Scan Date: {scan_data.get('scan_date', 'N/A')}
Overall Score: {scan_data.get('overall_score', 0):.1f}%
Grade: {scan_data.get('grade', 'N/A')}
Status: {scan_data.get('status', 'N/A')}

{'-'*70}
FINDINGS SUMMARY
{'-'*70}

"""
    
    # Add findings count by category
    findings = scan_data.get('findings', {})
    if findings:
        for category, count in findings.items():
            if isinstance(count, int):
                report += f"{category}: {count} issue(s)\n"
            elif isinstance(count, list):
                report += f"{category}: {len(count)} issue(s)\n"
                for item in count:
                    report += f"  • {item}\n"
    else:
        report += "No findings recorded\n"
    
    # Add detailed findings list if available
    detailed_findings = scan_data.get('detailed_findings', [])
    if detailed_findings:
        report += f"\n{'-'*70}\nDETAILED FINDINGS\n{'-'*70}\n\n"
        for i, finding in enumerate(detailed_findings, 1):
            report += f"{i}. [{finding.get('severity', 'medium').upper()}] {finding.get('category', 'N/A')}\n"
            report += f"   Issue: {finding.get('issue', 'N/A')}\n"
            report += f"   Recommendation: {finding.get('recommendation', 'N/A')}\n\n"
    
    # Add recommendations
    recommendations = scan_data.get('recommendations', [])
    if recommendations:
        report += f"\n{'-'*70}\nRECOMMENDATIONS FOR IMPROVEMENT\n{'-'*70}\n\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
    else:
        report += f"\n{'-'*70}\nRECOMMENDATIONS\n{'-'*70}\nNo recommendations - site is fully compliant! ✓\n"
    
    # Add AI analysis if available
    ai_analysis = scan_data.get('ai_analysis', '')
    if ai_analysis:
        report += f"\n{'-'*70}\nAI ANALYSIS\n{'-'*70}\n\n{ai_analysis}\n"
    
    report += f"\n{'='*70}\nReport generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*70}\n"
    
    return report


def export_scan_to_pdf(scan_data: Dict[str, Any]) -> bytes:
    """
    Export scan result to PDF format using ReportLab.
    
    Args:
        scan_data: Scan result dictionary
        
    Returns:
        PDF as bytes
    """
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#00d9ff'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#58a6ff'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#e6edf3'),
        spaceAfter=4
    )
    
    # Title
    story.append(Paragraph("GDPR/CCPA Compliance Scan Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Metadata table
    metadata = [
        ['URL', scan_data.get('url', 'N/A')],
        ['Scan Date', scan_data.get('scan_date', 'N/A')],
        ['Overall Score', f"{scan_data.get('overall_score', 0):.1f}%"],
        ['Grade', scan_data.get('grade', 'N/A')],
        ['Status', scan_data.get('status', 'N/A')],
    ]
    
    metadata_table = Table(metadata, colWidths=[1.5*inch, 4.5*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e2130')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#e6edf3')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2a3250')),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Findings Summary
    story.append(Paragraph("Findings Summary", heading_style))
    
    findings = scan_data.get('findings', {})
    if findings:
        findings_data = [['Category', 'Count']]
        for category, count in findings.items():
            if isinstance(count, int):
                findings_data.append([category, str(count)])
            elif isinstance(count, list):
                findings_data.append([category, str(len(count))])
        
        findings_table = Table(findings_data, colWidths=[3*inch, 2*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#58a6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f1520')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2a3250')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#1e2130'), colors.HexColor('#0f1520')]),
        ]))
        
        story.append(findings_table)
    else:
        story.append(Paragraph("No findings recorded", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations for Improvement", heading_style))
    
    recommendations = scan_data.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
    else:
        story.append(Paragraph("No recommendations - site is fully compliant! ✓", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # AI Analysis
    ai_analysis = scan_data.get('ai_analysis', '')
    if ai_analysis:
        story.append(Paragraph("AI Analysis", heading_style))
        # Split analysis into paragraphs for better formatting
        for paragraph in ai_analysis.split('\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Footer
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    
    # Build PDF
    doc.build(story)
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


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


# Aliases for convenience
export_batch_results_csv = export_batch_results_to_csv
export_json = export_scan_to_json
