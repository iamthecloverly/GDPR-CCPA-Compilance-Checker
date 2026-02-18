"""Dashboard page - landing page with quick stats and recent scans."""

import streamlit as st
from typing import Dict, Any
from components import render_header, render_stats_row
from database.operations import get_recent_scans, get_scan_statistics
from logger_config import get_logger

logger = get_logger(__name__)


def render_dashboard_page():
    """Render the dashboard landing page."""
    render_header()
    
    st.markdown("# 📊 Dashboard")
    st.markdown("*Quick overview of your compliance scanning activity*")
    
    # Get statistics from database
    try:
        stats = get_scan_statistics()
        render_stats_row({
            "total_scans": stats.get("total_scans", 0),
            "avg_score": stats.get("avg_score", 0),
            "compliant_count": stats.get("compliant_count", 0),
            "at_risk_count": stats.get("at_risk_count", 0),
        })
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        st.info("📊 Statistics will be available after your first scan")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📱 Quick Scan", key="dashboard_quick", use_container_width=True):
            st.session_state.page = "quick_scan"
            st.rerun()
    
    with col2:
        if st.button("📦 Batch Scan", key="dashboard_batch", use_container_width=True):
            st.session_state.page = "batch_scan"
            st.rerun()
    
    with col3:
        if st.button("📜 Scan History", key="dashboard_history", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
    
    st.markdown("---")
    
    # Recent scans
    st.markdown("### 📋 Recent Scans")
    
    try:
        recent_scans = get_recent_scans(limit=5)
        
        if recent_scans:
            for scan in recent_scans:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{scan.get('url', 'Unknown')}**")
                    
                    with col2:
                        score = scan.get('score', 0)
                        st.markdown(f"`{score}` / 100")
                    
                    with col3:
                        grade = scan.get('grade', 'N/A')
                        st.markdown(f"Grade: **{grade}**")
                    
                    with col4:
                        if st.button("View", key=f"view_{scan.get('id', 'unknown')}", use_container_width=True):
                            st.session_state.selected_scan_id = scan.get('id')
                            st.session_state.page = "view_scan"
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No scans yet. Start by performing a quick scan!")
    
    except Exception as e:
        logger.error(f"Error loading recent scans: {e}")
        st.warning("Could not load recent scans. Try refreshing the page.")
    
    # Help section
    with st.expander("❓ Help & Getting Started"):
        st.markdown("""
        **How to use this tool:**
        
        1. **Quick Scan** - Enter a single URL to check its GDPR/CCPA compliance
        2. **Batch Scan** - Upload multiple URLs at once for bulk scanning
        3. **Scan History** - View, filter, and analyze all previous scans
        4. **Settings** - Configure API keys and scanning preferences
        
        **What we check for:**
        - 🍪 Cookie consent mechanisms
        - 📄 Privacy policy presence and quality
        - 📧 Contact information (email, postal address)
        - 🔍 Third-party tracker detection
        
        **Need help?** Visit our documentation or contact support.
        """)


def main():
    """Main function for dashboard page."""
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    render_dashboard_page()


if __name__ == "__main__":
    main()
