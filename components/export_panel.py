"""Export and report generation components."""

import streamlit as st
from typing import Dict, Any, List, Optional, Literal
from libs.export import (
    export_scan_to_csv,
    export_batch_results_to_csv,
    export_scan_to_json,
    export_scan_to_pdf,
    format_full_scan_text
)
import logging

logger = logging.getLogger(__name__)


def render_export_panel(
    data: Dict[str, Any] | List[Dict[str, Any]],
    mode: Literal["single", "batch", "history"] = "single",
    title: str = "📥 Export Results",
    key_prefix: str = "export"
):
    """
    Unified export panel for scan results with responsive layout.
    Provides three export options: Copy Full Results, Download CSV, Download PDF.
    
    Args:
        data: Single scan dict (mode="single") or list of scans (mode="batch"/"history")
        mode: "single" for one scan, "batch"/"history" for multiple scans
        title: Custom title for the export section
        key_prefix: Prefix for Streamlit widget keys to avoid collisions
    """
    st.markdown(f"### {title}")
    
    # Use responsive 3-column layout (auto-responsive via CSS)
    col1, col2, col3 = st.columns(3, gap="medium")
    
    if mode == "single" and isinstance(data, dict):
        _render_single_scan_export(data, col1, col2, col3, key_prefix)
    elif mode in ["batch", "history"] and isinstance(data, list):
        _render_batch_export(data, col1, col2, col3, mode, key_prefix)
    else:
        st.error("Invalid data format for export mode")


def _render_single_scan_export(
    scan_result: Dict[str, Any],
    col_copy,
    col_csv,
    col_pdf,
    key_prefix: str
):
    """Render export buttons for a single scan result."""
    url_domain = scan_result.get('url', 'scan').replace('https://', '').replace('http://', '').replace('/', '_')[:30]
    
    # Column 1: Copy Full Results
    with col_copy:
        if st.button("📋 Copy Full Results", key=f"{key_prefix}_copy", use_container_width=True):
            try:
                text_report = format_full_scan_text(scan_result)
                st.code(text_report, language="text")
                st.success("✅ Copy the text above")
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                logger.error(f"Error copying text: {e}")
    
    # Column 2: Download CSV
    with col_csv:
        try:
            csv_data = export_scan_to_csv(scan_result)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"compliance_{url_domain}.csv",
                mime="text/csv",
                key=f"{key_prefix}_csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ CSV Error: {str(e)}")
            logger.error(f"Error exporting CSV: {e}")
    
    # Column 3: Download PDF
    with col_pdf:
        try:
            pdf_data = export_scan_to_pdf(scan_result)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_data,
                file_name=f"compliance_{url_domain}.pdf",
                mime="application/pdf",
                key=f"{key_prefix}_pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ PDF Error: {str(e)}")
            logger.error(f"Error exporting PDF: {e}")


def _render_batch_export(
    scan_results: List[Dict[str, Any]],
    col_copy,
    col_csv,
    col_pdf,
    mode: str,
    key_prefix: str
):
    """Render export buttons for batch/history scan results."""
    file_prefix = "batch_compliance" if mode == "batch" else "scan_history"
    
    # Column 1: Copy Summary
    with col_copy:
        if st.button("📋 Copy Summary", key=f"{key_prefix}_copy", use_container_width=True):
            try:
                # Create a summary text for batch results
                summary_text = f"Batch Compliance Scan Summary\n{'='*60}\n\nTotal Scans: {len(scan_results)}\n\n"
                for i, scan in enumerate(scan_results, 1):
                    summary_text += f"{i}. URL: {scan.get('url', 'N/A')}\n"
                    summary_text += f"   Score: {scan.get('overall_score', 0):.1f}% | Grade: {scan.get('grade', 'N/A')}\n\n"
                
                st.code(summary_text, language="text")
                st.success("✅ Copy the summary above")
            except Exception as e:
                st.error(f"❌ Error generating summary: {str(e)}")
                logger.error(f"Error copying batch summary: {e}")
    
    # Column 2: Download CSV
    with col_csv:
        try:
            csv_data = export_batch_results_to_csv(scan_results)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"{file_prefix}.csv",
                mime="text/csv",
                key=f"{key_prefix}_csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ CSV Error: {str(e)}")
            logger.error(f"Error exporting batch CSV: {e}")
    
    # Column 3: Download JSON
    with col_pdf:
        try:
            json_data = export_scan_to_json({
                "mode": mode,
                "total_scans": len(scan_results),
                "scans": scan_results
            })
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"{file_prefix}.json",
                mime="application/json",
                key=f"{key_prefix}_json",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ JSON Error: {str(e)}")
            logger.error(f"Error exporting batch JSON: {e}")


# Backward compatibility: Keep old function names pointing to new unified function
def render_export_options(scan_result: Dict[str, Any]):
    """
    [DEPRECATED] Use render_export_panel() instead.
    Render export options for a single scan.
    """
    render_export_panel(scan_result, mode="single", title="📥 Export Results", key_prefix="export_single")


def render_batch_export_options(scan_results: List[Dict[str, Any]]):
    """
    [DEPRECATED] Use render_export_panel() instead.
    Render export options for batch scan results.
    """
    render_export_panel(scan_results, mode="batch", title="📥 Export Batch Results", key_prefix="export_batch")


def render_history_export(scans: List[Dict[str, Any]]):
    """
    [DEPRECATED] Use render_export_panel() instead.
    Render export options for scan history.
    """
    render_export_panel(scans, mode="history", title="📥 Export History", key_prefix="export_history")
