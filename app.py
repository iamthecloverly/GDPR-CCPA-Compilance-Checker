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

# Minimal, clean CSS theme
st.markdown("""
<style>
    :root {
        --primary: #00d9ff;
        --bg-dark: #0a0e27;
        --bg-surface: #1a1f3a;
        --text-primary: #f5f7fa;
        --text-secondary: #b4bcd4;
        --border-color: #2a3250;
    }
    
    [data-testid="stApp"], body {
        background: var(--bg-dark);
        color: var(--text-primary);
    }
    
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { background: var(--bg-surface); border-right: 1px solid var(--border-color); }
    
    h1 { color: var(--primary); font-size: 2.5rem; margin-bottom: 0.5rem; }
    h2 { color: var(--text-primary); }
    h3 { color: var(--text-primary); }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), #00b8d4);
        color: #000;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 217, 255, 0.4); }
    
    .stButton > button[kind="secondary"] {
        background: var(--bg-surface);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    input, textarea, select {
        background: var(--bg-surface);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    input:focus, textarea:focus { border-color: var(--primary); outline: none; }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 31, 58, 0.95), rgba(15, 19, 26, 0.95));
        border-radius: 12px;
        padding: 1.5rem;
        border-top: 3px solid;
    }
    
    .metric-card.blue { border-top-color: #58a6ff; }
    .metric-card.green { border-top-color: #3fb950; }
    .metric-card.orange { border-top-color: #d29922; }
    .metric-card.red { border-top-color: #f85149; }
    
    [data-testid="metric-container"] {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
NAV_PAGES = {
    "dashboard": ("📊", "Dashboard"),
    "quick_scan": ("🔍", "Quick Scan"),
    "batch_scan": ("📂", "Batch Scan"),
    "history": ("📅", "History"),
}

if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def render_sidebar_navigation():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("## 🔒 Privacy Scanner")
        st.markdown("*GDPR & CCPA Compliance*")
        st.divider()
        
        for page_id, (icon, title) in NAV_PAGES.items():
            if st.button(f"{icon}  {title}", key=f"nav_{page_id}", use_container_width=True,
                        type="primary" if st.session_state.page == page_id else "secondary"):
                st.session_state.page = page_id
                st.rerun()
        
        st.divider()
        st.markdown("### Quick Stats")
        try:
            from database.operations import get_scan_statistics
            stats = get_scan_statistics()
            if stats:
                st.metric("Total Scans", stats.get("total_scans", 0))
                st.metric("Avg Score", f"{stats.get('avg_score', 0):.0f}/100")
        except:
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
