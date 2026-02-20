"""
GDPR/CCPA Compliance Checker - Modern Professional Interface

A production-ready privacy compliance scanner with AI-powered analysis,
real-time scanning, and comprehensive reporting capabilities.
"""

import streamlit as st
import os
import sys

# Setup base path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and logger
from logger_config import setup_logging, get_logger

# Import page modules
from pages.dashboard import render_dashboard_page as render_dashboard
from pages.quick_scan import render_quick_scan_page as render_scan_single
from pages.batch_scan import render_batch_scan_page as render_scan_batch
from pages.history import render_history_page as render_scan_history

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="Privacy Compliance Scanner",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "GDPR/CCPA Compliance Checker"
    }
)

# Custom CSS for elements not covered by Streamlit theme
st.markdown("""
<style>
    /* --- Metric cards (custom HTML from create_metric_card) --- */
    .metric-card {
        background: #1a1f3a;
        border-radius: 12px;
        padding: 1.25rem;
        border-top: 3px solid;
    }
    .metric-card.blue  { border-top-color: #58a6ff; }
    .metric-card.green { border-top-color: #3fb950; }
    .metric-card.orange{ border-top-color: #d29922; }
    .metric-card.red   { border-top-color: #f85149; }
    .metric-label {
        font-size: 0.85rem;
        color: #b4bcd4;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f5f7fa;
        line-height: 1.2;
    }
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 0.4rem;
        color: #b4bcd4;
    }
    .metric-delta.blue  { color: #58a6ff; }
    .metric-delta.green { color: #3fb950; }
    .metric-delta.orange{ color: #d29922; }
    .metric-delta.red   { color: #f85149; }

    /* --- Action cards (dashboard quick actions) --- */
    .action-card {
        background: #1a1f3a;
        border: 1px solid #2a3250;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    .action-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .action-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f5f7fa;
        margin: 0.5rem 0 0.25rem;
    }
    .action-desc {
        font-size: 0.85rem;
        color: #b4bcd4;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
NAV_PAGES = {
    "dashboard": "Dashboard",
    "quick_scan": "Quick Scan",
    "batch_scan": "Batch Scan",
    "history": "History",
}

if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def render_sidebar_navigation():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("## Privacy Scanner")
        st.markdown("*GDPR & CCPA Compliance*")
        st.divider()

        page_ids = list(NAV_PAGES.keys())
        page_labels = list(NAV_PAGES.values())
        current_index = page_ids.index(st.session_state.page) if st.session_state.page in page_ids else 0

        selected_label = st.radio(
            "Navigation",
            page_labels,
            index=current_index,
            label_visibility="collapsed",
        )

        selected_id = page_ids[page_labels.index(selected_label)]
        if selected_id != st.session_state.page:
            st.session_state.page = selected_id
            st.rerun()

        st.divider()
        st.markdown("### Quick Stats")
        try:
            from database.operations import get_scan_statistics
            stats = get_scan_statistics()
            if stats:
                st.metric("Total Scans", stats.get("total_scans", 0))
                st.metric("Avg Score", f"{stats.get('avg_score', 0):.0f}/100")
        except Exception:
            st.caption("No scans yet")


def main():
    """Main application router."""
    render_sidebar_navigation()
    
    if st.session_state.page == "dashboard":
        render_dashboard()
    elif st.session_state.page == "quick_scan":
        render_scan_single()
    elif st.session_state.page == "batch_scan":
        render_scan_batch()
    elif st.session_state.page == "history":
        render_scan_history()
    else:
        st.error(f"Unknown page: {st.session_state.page}")
        st.session_state.page = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()
