"""Export and report generation components."""

import streamlit as st
from typing import Dict, Any, List
from libs.export import export_scan_to_csv, export_batch_results_csv, export_json
import logging

logger = logging.getLogger(__name__)


def render_export_options(scan_result: Dict[str, Any]):
    """
    Render export options for a single scan.
    
    Args:
        scan_result: Scan result dictionary
    """
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download CSV", key="export_csv", width='stretch'):
            try:
                csv_data = export_scan_to_csv(scan_result)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"compliance_report_{scan_result.get('url', 'scan').replace('https://', '').replace('/', '_')}.csv",
                    mime="text/csv",
                    key="csv_download"
                )
                st.success("CSV exported successfully!")
            except Exception as e:
                st.error(f"Error exporting CSV: {str(e)}")
    
    with col2:
        if st.button("📋 Download JSON", key="export_json", width='stretch'):
            try:
                json_data = export_json(scan_result)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"compliance_report_{scan_result.get('url', 'scan').replace('https://', '').replace('/', '_')}.json",
                    mime="application/json",
                    key="json_download"
                )
                st.success("JSON exported successfully!")
            except Exception as e:
                st.error(f"Error exporting JSON: {str(e)}")
    
    with col3:
        if st.button("🔗 Copy as Text", key="export_text", width='stretch'):
            try:
                text_report = format_text_report(scan_result)
                st.code(text_report, language="text")
                st.info("📋 Copy from the code block above")
            except Exception as e:
                st.error(f"Error generating text report: {str(e)}")


def render_batch_export_options(scan_results: List[Dict[str, Any]]):
    """
    Render export options for batch scan results.
    
    Args:
        scan_results: List of scan result dictionaries
    """
    st.markdown("### 📥 Export Batch Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download CSV", key="export_batch_csv", width='stretch'):
            try:
                csv_data = export_batch_results_csv(scan_results)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="batch_compliance_report.csv",
                    mime="text/csv",
                    key="batch_csv_download"
                )
                st.success("Batch CSV exported successfully!")
            except Exception as e:
                st.error(f"Error exporting batch CSV: {str(e)}")
    
    with col2:
        if st.button("📋 Download JSON", key="export_batch_json", width='stretch'):
            try:
                json_data = export_json({"batch_results": scan_results})
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="batch_compliance_report.json",
                    mime="application/json",
                    key="batch_json_download"
                )
                st.success("Batch JSON exported successfully!")
            except Exception as e:
                st.error(f"Error exporting batch JSON: {str(e)}")


def format_text_report(scan: Dict[str, Any]) -> str:
    """
    Format scan result as readable text report.
    
    Args:
        scan: Scan result dictionary
        
    Returns:
        Formatted text report
    """
    report = f"""
GDPR/CCPA COMPLIANCE SCAN REPORT
{'='*60}

Website URL: {scan.get('url', 'N/A')}
Scan Date: {scan.get('scan_date', 'N/A')}
Overall Score: {scan.get('score', 0)}/100
Grade: {scan.get('grade', 'N/A')}
Status: {scan.get('status', 'N/A')}

SCORE BREAKDOWN
{'-'*60}
"""
    
    breakdown = scan.get('score_breakdown', {})
    if breakdown:
        for category, points in breakdown.items():
            report += f"{category}: {points} points\n"
    else:
        report += "No breakdown data available\n"
    
    report += f"\n\nKEY FINDINGS\n{'-'*60}\n"
    
    findings = scan.get('findings', {})
    if findings:
        for category, items in findings.items():
            report += f"\n{category.replace('_', ' ').title()}:\n"
            if items:
                for item in items:
                    report += f"  • {item}\n"
            else:
                report += "  ✓ No issues found\n"
    else:
        report += "No findings recorded\n"
    
    recommendations = scan.get('recommendations', [])
    if recommendations:
        report += f"\n\nRECOMMENDATIONS\n{'-'*60}\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
    
    return report


def render_history_export(scans: List[Dict[str, Any]]):
    """
    Render export options for scan history.
    
    Args:
        scans: List of historical scan results
    """
    st.markdown("### 📥 Export History")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export as CSV", key="export_history_csv"):
            try:
                csv_data = export_batch_results_csv(scans)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="scan_history.csv",
                    mime="text/csv",
                    key="history_csv_download"
                )
            except Exception as e:
                st.error(f"Error exporting: {str(e)}")
    
    with col2:
        if st.button("📋 Export as JSON", key="export_history_json"):
            try:
                json_data = export_json({"scan_history": scans, "total_scans": len(scans)})
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="scan_history.json",
                    mime="application/json",
                    key="history_json_download"
                )
            except Exception as e:
                st.error(f"Error exporting: {str(e)}")
