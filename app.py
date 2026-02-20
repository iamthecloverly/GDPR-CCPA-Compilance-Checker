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
from app_pages.dashboard import render_dashboard_page as render_dashboard
from app_pages.quick_scan import render_quick_scan_page as render_scan_single
from app_pages.batch_scan import render_batch_scan_page as render_scan_batch
from app_pages.history import render_history_page as render_scan_history

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

# Custom CSS for sidebar nav and custom HTML elements
st.markdown("""
<style>
    /* --- Sidebar nav buttons: look like links, not CTAs --- */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #b4bcd4 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.75rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
        transform: none !important;
        transition: background 0.15s, color 0.15s !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 217, 255, 0.08) !important;
        color: #f5f7fa !important;
        box-shadow: none !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(0, 217, 255, 0.12) !important;
        color: #00d9ff !important;
        font-weight: 600 !important;
        border-left: 3px solid #00d9ff !important;
        border-radius: 0 8px 8px 0 !important;
    }
    /* Sidebar stats: strip default metric card chrome */
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        border: none !important;
        background: transparent !important;
        padding: 0.25rem 0 !important;
    }

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

    /* --- Hero Section --- */
    .hero-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        padding: 3.5rem 2.5rem;
        background: linear-gradient(135deg, #0a0e27 0%, #0d1135 60%, #111827 100%);
        border-radius: 16px;
        border: 1px solid #1e2647;
        margin-bottom: 2.5rem;
        gap: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero-glow-top {
        position: absolute; top: -100px; right: -100px;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(0,217,255,0.07) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-glow-bottom {
        position: absolute; bottom: -80px; left: -80px;
        width: 250px; height: 250px;
        background: radial-gradient(circle, rgba(88,166,255,0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-content { flex: 1; max-width: 580px; position: relative; z-index: 1; }
    .hero-badge {
        display: inline-block;
        background: rgba(0,217,255,0.1);
        border: 1px solid rgba(0,217,255,0.3);
        color: #00d9ff;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        margin-bottom: 1.25rem;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0 0 1rem;
        background: linear-gradient(135deg, #f5f7fa 30%, #00d9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #8b949e;
        line-height: 1.7;
        margin: 0 0 1.75rem;
        max-width: 460px;
    }
    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-bottom: 2rem;
    }
    .hero-pill {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: #c9d1d9;
        font-size: 0.8rem;
        padding: 0.28rem 0.8rem;
        border-radius: 20px;
    }
    .hero-visual { flex-shrink: 0; position: relative; z-index: 1; }

    /* --- Section eyebrow labels --- */
    .section-eyebrow {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #00d9ff;
        margin-bottom: 0.2rem;
    }
    .section-heading {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f5f7fa;
        margin: 0 0 1.1rem;
    }

    /* --- Mobile responsiveness --- */
    @media (max-width: 768px) {
        .hero-section {
            flex-direction: column;
            padding: 2rem 1.25rem;
            gap: 1.5rem;
        }
        .hero-title { font-size: 1.9rem; }
        .hero-subtitle { font-size: 0.95rem; max-width: 100%; }
        .hero-content { max-width: 100%; }
        .hero-visual { display: none; }
        .metric-card { padding: 1rem; }
        .metric-value { font-size: 1.5rem; }
        .action-card { padding: 1rem; }
        .section-heading { font-size: 1.1rem; }
    }
    @media (max-width: 480px) {
        .hero-title { font-size: 1.55rem; }
        .hero-badge { font-size: 0.65rem; }
        .hero-section { padding: 1.5rem 1rem; }
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
        # Navigation buttons styled as links via CSS
        for page_id, label in NAV_PAGES.items():
            is_active = st.session_state.page == page_id
            if st.button(
                label,
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = page_id
                st.rerun()

        st.divider()

        # Compact quick stats
        st.markdown(
            '<div style="font-size:0.72rem; color:#b4bcd4; text-transform:uppercase; '
            'letter-spacing:0.08em; padding: 0 0.25rem 0.5rem;">Quick Stats</div>',
            unsafe_allow_html=True,
        )
        try:
            from database.operations import get_scan_statistics
            stats = get_scan_statistics()
            if stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Scans", stats.get("total_scans", 0))
                with col2:
                    st.metric("Avg", f"{stats.get('avg_score', 0):.0f}")
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
