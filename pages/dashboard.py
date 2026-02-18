"""Dashboard page - landing page with statistics and quick start."""

import streamlit as st
from typing import Dict, Any
from components import render_header, render_stats_row
from database.operations import get_recent_scans, get_scan_statistics
from logger_config import get_logger

logger = get_logger(__name__)


def render_dashboard_page():
    """Render the dashboard landing page."""
    render_header()
    
    st.markdown("# Dashboard")
    st.markdown("Your compliance scanning hub - View stats, recent scans, and quick actions")
    st.divider()
    
    # Statistics section with error handling
    st.markdown("### Compliance Overview")
    
    try:
        stats = get_scan_statistics()
        if stats:
            render_stats_row({
                "total_scans": stats.get("total_scans", 0),
                "avg_score": stats.get("avg_score", 0),
                "compliant_count": stats.get("compliant_count", 0),
                "at_risk_count": stats.get("at_risk_count", 0),
            })
        else:
            st.info("💡 No scans yet. Start by running a quick scan to see your first compliance report.")
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        st.info("💡 Statistics will appear after your first compliance scan")
    
    st.divider()
    
    # Quick start actions
    st.markdown("### Quick Start")
    st.markdown("Choose how you want to scan for compliance:")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("\n")
        if st.button("Quick Scan", key="dash_quick", use_container_width=True, type="primary"):
            st.session_state.page = "quick_scan"
            st.rerun()
        st.caption("Scan a single website")
    
    with col2:
        st.markdown("\n")
        if st.button("Batch Scan", key="dash_batch", use_container_width=True, type="primary"):
            st.session_state.page = "batch_scan"
            st.rerun()
        st.caption("Scan multiple websites")
    
    with col3:
        st.markdown("\n")
        if st.button("View History", key="dash_history", use_container_width=True, type="primary"):
            st.session_state.page = "history"
            st.rerun()
        st.caption("View past scans")
    
    st.divider()
    
    # Recent scans list
    st.markdown("### Recent Scans")
    
    try:
        recent_scans = get_recent_scans(limit=5)
        
        if recent_scans:
            for idx, scan in enumerate(recent_scans):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1.5])
                    
                    with col1:
                        st.markdown(f"**{scan.get('url', 'Unknown URL')}**")
                        st.caption(f"Scanned: {scan.get('scan_date', 'N/A')}")
                    
                    with col2:
                        score = scan.get('score', 0)
                        st.metric("Score", f"{score}/100")
                    
                    with col3:
                        grade = scan.get('grade', 'N/A')
                        if grade == 'A':
                            grade_color = '#10b981'
                        elif grade in ['B', 'C']:
                            grade_color = '#f59e0b'
                        else:
                            grade_color = '#ef4444'
                        st.markdown(f"<span style='color: {grade_color}; font-weight: bold; font-size: 18px;'>Grade {grade}</span>", unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("View Details", key=f"details_{idx}", use_container_width=True, type="secondary"):
                            st.session_state.selected_scan_id = scan.get('id')
                            st.session_state.page = "history"
                            st.rerun()
        else:
            st.info("No scans yet. Start with a quick scan above!")
    except Exception as e:
        logger.warning(f"Error fetching recent scans: {e}")
        st.info("Recent scans will appear after your first scan")
    
    st.divider()
    
    # Help section
    with st.expander("Help & Getting Started"):
        st.markdown("""
        **How to use this tool:**
        
        1. **Quick Scan** - Enter a single URL to check its GDPR/CCPA compliance
        2. **Batch Scan** - Upload multiple URLs at once for bulk scanning
        3. **Scan History** - View, filter, and analyze all previous scans
        
        **What we check for:**
        - Cookie consent mechanisms
        - Privacy policy presence and quality
        - Contact information (email, postal address)
        - Third-party tracker detection
        
        **Compliance Grades:**
        - **Grade A** - Excellent compliance (80-100 points)
        - **Grade B/C** - Moderate issues, needs review (60-79 points)
        - **Grade D/F** - Critical issues, urgent action needed (0-59 points)
        """)


def main():
    """Main function for dashboard page."""
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    render_dashboard_page()


if __name__ == "__main__":
    main()
