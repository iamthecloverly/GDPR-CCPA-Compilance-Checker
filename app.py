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
    /* ── Animations ───────────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(22px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50%       { transform: translateY(-10px); }
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.45; transform: scale(0.75); }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(0,217,255,0.35); }
        50%       { box-shadow: 0 0 0 7px rgba(0,217,255,0); }
    }
    @keyframes shimmer {
        0%   { background-position: -400% center; }
        100% { background-position:  400% center; }
    }

    /* ── Sidebar nav buttons ───────────────────────────────────── */
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
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        border: none !important; background: transparent !important; padding: 0.25rem 0 !important;
    }

    /* ── Metric cards ──────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(145deg, #1a1f3a 0%, #161b33 100%);
        border-radius: 14px;
        padding: 1.35rem;
        border-top: 3px solid;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: default;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
    }
    .metric-card.blue   { border-top-color: #58a6ff; }
    .metric-card.green  { border-top-color: #3fb950; }
    .metric-card.orange { border-top-color: #d29922; }
    .metric-card.red    { border-top-color: #f85149; }
    .metric-label {
        font-size: 0.78rem; color: #8b949e; margin-bottom: 0.45rem;
        text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem; font-weight: 800; color: #f5f7fa; line-height: 1.1;
    }
    .metric-delta { font-size: 0.78rem; margin-top: 0.45rem; color: #8b949e; }
    .metric-delta.blue   { color: #58a6ff; }
    .metric-delta.green  { color: #3fb950; }
    .metric-delta.orange { color: #d29922; }
    .metric-delta.red    { color: #f85149; }

    /* ── Action cards ──────────────────────────────────────────── */
    .action-card {
        background: linear-gradient(145deg, #1a1f3a 0%, #161b33 100%);
        border: 1px solid #2a3250;
        border-radius: 14px;
        padding: 1.6rem;
        text-align: center;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .action-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 30px rgba(0,0,0,0.4);
        border-color: rgba(0,217,255,0.22);
    }
    .action-icon  { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .action-title { font-size: 1.05rem; font-weight: 700; color: #f5f7fa; margin: 0.5rem 0 0.3rem; }
    .action-desc  { font-size: 0.83rem; color: #8b949e; margin: 0; line-height: 1.5; }

    /* ── Main-area primary button glow ─────────────────────────── */
    [data-testid="stMain"] .stButton > button[kind="primary"] {
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stMain"] .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(0,217,255,0.38) !important;
    }

    /* ── Hero Section ──────────────────────────────────────────── */
    .hero-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        padding: 4rem 3rem;
        background: linear-gradient(135deg, #080c20 0%, #0b1030 55%, #0f1520 100%);
        border-radius: 20px;
        border: 1px solid #1e2647;
        box-shadow: 0 0 60px rgba(0,217,255,0.06), 0 20px 60px rgba(0,0,0,0.5);
        margin-bottom: 2.5rem;
        gap: 2.5rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.65s ease both;
    }
    /* Dot-grid overlay */
    .hero-section::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image: radial-gradient(rgba(0,217,255,0.10) 1px, transparent 1px);
        background-size: 30px 30px;
        pointer-events: none;
        border-radius: inherit;
    }
    /* Cyan glow top-right */
    .hero-glow-top {
        position: absolute; top: -120px; right: -120px;
        width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(0,217,255,0.09) 0%, transparent 65%);
        pointer-events: none;
    }
    /* Blue glow bottom-left */
    .hero-glow-bottom {
        position: absolute; bottom: -100px; left: -100px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(88,166,255,0.07) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-content { flex: 1; max-width: 580px; position: relative; z-index: 1; }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(0,217,255,0.08);
        border: 1px solid rgba(0,217,255,0.28);
        color: #00d9ff;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.32rem 0.9rem;
        border-radius: 20px;
        margin-bottom: 1.35rem;
    }
    .hero-live-dot {
        display: inline-block;
        width: 6px; height: 6px;
        background: #00d9ff;
        border-radius: 50%;
        animation: pulseDot 2s ease-in-out infinite;
        flex-shrink: 0;
    }
    .hero-title {
        font-size: 3.1rem;
        font-weight: 900;
        line-height: 1.1;
        margin: 0 0 1.1rem;
        background: linear-gradient(135deg, #ffffff 20%, #a8d8ff 60%, #00d9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.08rem;
        color: #7d8ba3;
        line-height: 1.75;
        margin: 0 0 1.75rem;
        max-width: 480px;
    }
    .hero-pills {
        display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0;
    }
    .hero-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        color: #9dafc8;
        font-size: 0.78rem;
        padding: 0.26rem 0.75rem;
        border-radius: 20px;
        transition: border-color 0.2s, color 0.2s;
    }
    .hero-pill:hover { border-color: rgba(0,217,255,0.3); color: #c9d1d9; }
    /* Floating SVG */
    .hero-visual { flex-shrink: 0; position: relative; z-index: 1; }
    .hero-visual svg { animation: float 5.5s ease-in-out infinite; display: block; }

    /* ── Trust strip ────────────────────────────────────────────── */
    .trust-strip {
        display: flex; align-items: center; gap: 1.5rem;
        flex-wrap: wrap; margin-top: 0.25rem;
    }
    .trust-item {
        display: flex; align-items: center; gap: 0.35rem;
        font-size: 0.8rem; color: #6b7a96;
    }
    .trust-value { color: #c9d1d9; font-weight: 700; }
    .trust-sep {
        width: 1px; height: 14px;
        background: #2a3250; flex-shrink: 0;
    }

    /* ── Section eyebrow labels ────────────────────────────────── */
    .section-eyebrow {
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.13em;
        text-transform: uppercase; color: #00d9ff; margin-bottom: 0.15rem;
    }
    .section-heading {
        font-size: 1.35rem; font-weight: 700; color: #f5f7fa; margin: 0 0 1.1rem;
        letter-spacing: -0.01em;
    }

    /* ── Mobile ─────────────────────────────────────────────────── */
    @media (max-width: 768px) {
        .hero-section { flex-direction: column; padding: 2.25rem 1.5rem; gap: 1.5rem; }
        .hero-title   { font-size: 2rem; }
        .hero-subtitle{ font-size: 0.95rem; max-width: 100%; }
        .hero-content { max-width: 100%; }
        .hero-visual  { display: none; }
        .metric-card  { padding: 1rem; }
        .metric-value { font-size: 1.6rem; }
        .action-card  { padding: 1.1rem; }
        .section-heading { font-size: 1.1rem; }
        .trust-strip  { gap: 0.85rem; }
    }
    @media (max-width: 480px) {
        .hero-title  { font-size: 1.65rem; }
        .hero-badge  { font-size: 0.62rem; }
        .hero-section{ padding: 1.75rem 1rem; }
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
