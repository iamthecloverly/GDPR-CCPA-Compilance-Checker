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
        padding: 5rem 3.5rem;
        background: linear-gradient(135deg, #080c20 0%, #0b1030 55%, #0f1520 100%);
        border-radius: 20px;
        border: 1px solid #1e2647;
        box-shadow: 0 0 60px rgba(0,217,255,0.06), 0 20px 60px rgba(0,0,0,0.5);
        margin-bottom: 3rem;
        gap: 3rem;
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
    .hero-content { flex: 1; min-width: 320px; max-width: 560px; position: relative; z-index: 1; }
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

    /* ── Hero CTA buttons ──────────────────────────────────────── */
    .hero-cta-row {
        display: flex; gap: 0.85rem; flex-wrap: wrap; margin: 2rem 0 2.5rem;
    }
    .hero-btn-primary {
        display: inline-flex; align-items: center; gap: 0.45rem;
        background: linear-gradient(135deg, #00b4d8, #0077b6);
        color: #fff; font-weight: 700; font-size: 0.92rem;
        padding: 0.75rem 1.6rem; border-radius: 10px;
        text-decoration: none;
        box-shadow: 0 4px 20px rgba(0,180,216,0.35);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .hero-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,180,216,0.5);
        color: #fff; text-decoration: none;
    }
    .hero-btn-secondary {
        display: inline-flex; align-items: center; gap: 0.45rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        color: #c9d1d9; font-weight: 600; font-size: 0.92rem;
        padding: 0.75rem 1.6rem; border-radius: 10px;
        text-decoration: none;
        transition: background 0.15s, border-color 0.15s, color 0.15s;
    }
    .hero-btn-secondary:hover {
        background: rgba(0,217,255,0.08);
        border-color: rgba(0,217,255,0.3);
        color: #f0f6fc; text-decoration: none;
    }

    /* ── Hero stats row ─────────────────────────────────────────── */
    .hero-stats {
        display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 0;
    }
    .hero-stat-item { display: flex; flex-direction: column; }
    .hero-stat-num {
        font-size: 1.65rem; font-weight: 800; color: #f5f7fa; line-height: 1;
    }
    .hero-stat-label {
        font-size: 0.72rem; color: #5a6a8a; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 0.2rem; font-weight: 600;
    }

    /* ── Product mockup card ────────────────────────────────────── */
    .hero-mockup {
        flex-shrink: 0; width: 380px; position: relative; z-index: 1;
    }
    .mockup-window {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 24px 60px rgba(0,0,0,0.7), 0 0 0 1px #21262d;
    }
    .mockup-titlebar {
        background: #161b22;
        padding: 0.65rem 1rem;
        display: flex; align-items: center; gap: 0.5rem;
        border-bottom: 1px solid #21262d;
    }
    .mockup-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .mockup-dot.red    { background: #ff5f57; }
    .mockup-dot.yellow { background: #febc2e; }
    .mockup-dot.green  { background: #28c840; }
    .mockup-url {
        flex: 1; background: #0d1117; border: 1px solid #30363d;
        border-radius: 6px; padding: 0.22rem 0.65rem;
        font-size: 0.72rem; color: #8b949e; margin-left: 0.5rem;
    }
    .mockup-body { padding: 1.25rem 1.25rem 1.5rem; }
    .mockup-site-row {
        display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;
    }
    .mockup-favicon {
        width: 20px; height: 20px; border-radius: 4px;
        background: linear-gradient(135deg, #58a6ff, #1d60b5);
        flex-shrink: 0;
    }
    .mockup-site-name { font-size: 0.78rem; color: #8b949e; }
    .mockup-score-row {
        display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;
        padding: 0.85rem 1rem; background: #0a0f1e;
        border: 1px solid #1e2647; border-radius: 10px;
    }
    .mockup-grade {
        width: 52px; height: 52px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; font-weight: 900; flex-shrink: 0;
        background: rgba(63,185,80,0.12); border: 2px solid #3fb950; color: #3fb950;
    }
    .mockup-score-num { font-size: 1.6rem; font-weight: 800; color: #f0f6fc; line-height: 1; }
    .mockup-score-sub { font-size: 0.7rem; color: #8b949e; margin-top: 0.15rem; }
    .mockup-status-badge {
        font-size: 0.65rem; font-weight: 700; padding: 0.18rem 0.55rem;
        border-radius: 20px; background: rgba(63,185,80,0.12);
        border: 1px solid rgba(63,185,80,0.3); color: #3fb950;
        display: inline-flex; align-items: center; gap: 0.25rem;
        margin-top: 0.25rem;
    }
    .mockup-findings { display: flex; flex-direction: column; gap: 0.45rem; }
    .mockup-finding {
        display: flex; align-items: center; gap: 0.6rem;
        font-size: 0.73rem; padding: 0.4rem 0.75rem;
        border-radius: 7px; color: #c9d1d9;
    }
    .mockup-finding.pass { background: rgba(63,185,80,0.06); border: 1px solid rgba(63,185,80,0.15); }
    .mockup-finding.warn { background: rgba(240,136,62,0.06); border: 1px solid rgba(240,136,62,0.15); color: #f0883e; }
    .mockup-finding.fail { background: rgba(248,81,73,0.06); border: 1px solid rgba(248,81,73,0.15); color: #f85149; }
    .mockup-finding-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .mockup-finding.pass .mockup-finding-dot { background: #3fb950; }
    .mockup-finding.warn .mockup-finding-dot { background: #f0883e; }
    .mockup-finding.fail .mockup-finding-dot { background: #f85149; }
    .mockup-glow {
        position: absolute; top: -60px; right: -60px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(0,217,255,0.06) 0%, transparent 70%);
        pointer-events: none; border-radius: 50%;
    }

    /* ── Section divider ─────────────────────────────────────────── */
    .hero-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #1e2647 25%, #1e2647 75%, transparent 100%);
        margin: 3rem 0;
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
        .hero-content { max-width: 100%; min-width: unset; }
        .hero-mockup  { display: none; }
        .hero-btn-primary, .hero-btn-secondary { font-size: 0.85rem; padding: 0.7rem 1.2rem; }
        .metric-card  { padding: 1rem; }
        .metric-value { font-size: 1.6rem; }
        .action-card  { padding: 1.1rem; }
        .section-heading { font-size: 1.1rem; }
    }
    @media (max-width: 480px) {
        .hero-title  { font-size: 1.65rem; }
        .hero-badge  { font-size: 0.62rem; }
        .hero-section{ padding: 1.75rem 1rem; }
    }

    /* ── Sidebar brand & structure ──────────────────────────────── */
    .sb-brand {
        display: flex; align-items: center; gap: 0.7rem;
        padding: 0.25rem 0.25rem 1rem;
    }
    .sb-logo {
        width: 38px; height: 38px; flex-shrink: 0;
        background: linear-gradient(135deg, rgba(0,217,255,0.15), rgba(88,166,255,0.2));
        border: 1px solid rgba(0,217,255,0.28);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
    }
    .sb-name {
        font-size: 0.98rem; font-weight: 700; color: #f0f4ff; line-height: 1.2;
        letter-spacing: -0.01em;
    }
    .sb-tag {
        font-size: 0.62rem; color: #556080; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 1px;
    }
    .sb-hr {
        height: 1px; background: #1a2040;
        margin: 0.4rem 0 0.75rem;
    }
    .sb-section-label {
        font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: #3d4f72;
        padding: 0 0.25rem 0.4rem;
    }
    .sb-stats-row {
        display: flex; gap: 0; margin: 0.25rem 0 0.75rem;
    }
    .sb-stat {
        flex: 1; text-align: center; padding: 0.65rem 0.25rem;
        background: #0f1428; border-radius: 8px; margin: 0 0.2rem;
    }
    .sb-stat-val {
        font-size: 1.2rem; font-weight: 800; color: #f0f4ff; line-height: 1;
    }
    .sb-stat-label {
        font-size: 0.6rem; color: #4a5a7a; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 3px;
    }
    .sb-footer {
        text-align: center; font-size: 0.62rem; color: #2e3d5a;
        padding: 0.5rem 0 0.25rem;
    }

    /* ── Spacing utilities ─────────────────────────────────────── */
    .section-space {
        margin: 1.5rem 0 !important;
    }
    .compact-space {
        margin: 0.75rem 0 !important;
    }
    .large-space {
        margin: 2rem 0 !important;
    }

    /* ── Component-specific styles ─────────────────────────────── */
    .score-display-container {
        text-align: center;
        padding: 20px;
        background: rgba(30, 33, 46, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(88, 166, 255, 0.1);
    }
    .score-display-value {
        font-size: 64px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .score-display-max {
        font-size: 14px;
        color: #a0aec0;
        margin-bottom: 15px;
    }
    .score-display-grade {
        font-size: 24px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .score-display-status {
        font-size: 12px;
        color: #e6edf3;
    }

    .stats-summary-box {
        background: rgba(30, 33, 46, 0.5);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(88, 166, 255, 0.08);
        font-size: 14px;
    }
    .stats-summary-item {
        margin-bottom: 10px;
    }
    .stats-summary-label {
        color: #a0aec0;
        display: block;
        margin-bottom: 3px;
    }
    .stats-summary-value {
        color: #e6edf3;
        word-break: break-all;
    }
    .stats-summary-value.status {
        font-weight: bold;
    }

    .ai-analysis-box {
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        background: rgba(0, 217, 255, 0.02);
        margin: 1.5rem 0;
    }
    .ai-analysis-title {
        color: #00d9ff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* ── Responsive media queries ──────────────────────────────── */
    @media (max-width: 768px) {
        .section-space {
            margin: 1rem 0 !important;
        }
        .compact-space {
            margin: 0.5rem 0 !important;
        }
        .large-space {
            margin: 1.5rem 0 !important;
        }
        /* Metric cards spacing adjustment for tablets */
        .metric-card {
            padding: 1rem !important;
        }
        /* Component responsiveness for tablets */
        .score-display-container {
            padding: 15px;
        }
        .score-display-value {
            font-size: 48px;
        }
        .score-display-grade {
            font-size: 18px;
        }
        .stats-summary-box {
            padding: 12px;
            font-size: 13px;
        }
        .ai-analysis-box {
            padding: 1rem;
        }
    }

    @media (max-width: 480px) {
        .section-space {
            margin: 0.75rem 0 !important;
        }
        .compact-space {
            margin: 0.25rem 0 !important;
        }
        .large-space {
            margin: 1rem 0 !important;
        }
        /* Mobile button sizing and spacing */
        .stButton > button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        /* Mobile component sizing */
        .score-display-container {
            padding: 12px;
        }
        .score-display-value {
            font-size: 36px;
        }
        .score-display-max {
            font-size: 12px;
        }
        .score-display-grade {
            font-size: 16px;
            margin-top: 8px;
        }
        .score-display-status {
            font-size: 11px;
        }
        .stats-summary-box {
            padding: 10px;
            font-size: 12px;
        }
        .stats-summary-item {
            margin-bottom: 8px;
        }
        .ai-analysis-box {
            padding: 0.8rem;
            margin: 1rem 0;
        }
        .ai-analysis-title {
            font-size: 1rem;
            margin-bottom: 0.8rem;
        }
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

# ── Query-param CTA routing ──────────────────────────────────────────
_nav = st.query_params.get("nav", "")
if _nav in NAV_PAGES:
    st.session_state.page = _nav
    st.query_params.clear()
    st.rerun()


def render_sidebar_navigation():
    """Render sidebar navigation."""
    with st.sidebar:
        # ── Brand header ──────────────────────────────────────────
        st.markdown("""
        <div class="sb-brand">
            <div class="sb-logo">🔒</div>
            <div>
                <div class="sb-name">PrivacyGuard</div>
                <div class="sb-tag">Compliance Platform</div>
            </div>
        </div>
        <div class="sb-hr"></div>
        <div class="sb-section-label">Navigation</div>
        """, unsafe_allow_html=True)

        # ── Nav items ─────────────────────────────────────────────
        NAV_ITEMS = [
            ("dashboard",  "⊞  Dashboard"),
            ("quick_scan", "⚡  Quick Scan"),
            ("batch_scan", "⊟  Batch Scan"),
            ("history",    "◷  History"),
        ]
        for page_id, label in NAV_ITEMS:
            is_active = st.session_state.page == page_id
            if st.button(
                label,
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Stats row ─────────────────────────────────────────────
        st.markdown('<div class="sb-hr" style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)
        try:
            from database.operations import get_scan_statistics
            stats = get_scan_statistics() or {}
            total = stats.get("total_scans", 0)
            avg = stats.get("avg_score", 0)
            st.markdown(f"""
            <div class="sb-stats-row">
                <div class="sb-stat">
                    <div class="sb-stat-val">{total}</div>
                    <div class="sb-stat-label">Scans</div>
                </div>
                <div class="sb-stat">
                    <div class="sb-stat-val">{avg:.0f}</div>
                    <div class="sb-stat-label">Avg Score</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

        # ── Footer ────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-footer">PrivacyGuard · GDPR &amp; CCPA</div>',
            unsafe_allow_html=True,
        )


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
