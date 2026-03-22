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

# Distinctive fonts: Syne (display) · DM Sans (body) · JetBrains Mono (data)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Custom CSS for sidebar nav and custom HTML elements
st.markdown("""
<style>
    /* ── Design tokens ──────────────────────────────────────────── */
    :root {
        --bg:            #05060b;
        --surface-1:     #0d0f1a;
        --surface-2:     #121520;
        --border:        #1c1f35;
        --border-bright: #282b44;
        --primary:       #f59e0b;
        --primary-dim:   rgba(245,158,11,0.10);
        --primary-glow:  rgba(245,158,11,0.28);
        --violet:        #8b5cf6;
        --violet-dim:    rgba(139,92,246,0.10);
        --success:       #10b981;
        --danger:        #f43f5e;
        --text-1:        #f0f4ff;
        --text-2:        #8892aa;
        --text-3:        #475570;
        --font-display:  'Syne', sans-serif;
        --font-body:     'DM Sans', sans-serif;
        --font-mono:     'JetBrains Mono', monospace;
        --r-sm:          8px;
        --r-md:          12px;
        --r-lg:          16px;
        --r-xl:          20px;
    }

    /* ── Apply DM Sans — targeted, preserving Material Icons ────── */
    html, body {
        font-family: var(--font-body) !important;
    }
    p, label, input, textarea, select,
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stText, .stCaption,
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"],
    [data-testid="stCaptionContainer"],
    [data-testid="stSidebarContent"],
    [data-testid="stMain"] p,
    [data-testid="stMain"] label {
        font-family: var(--font-body) !important;
    }
    /* Restore Material Symbols / Icons used by Streamlit toolbar */
    .material-icons,
    .material-symbols-rounded,
    [class*="material-icon"],
    [class*="material-symbol"],
    span[class*="Icon"],
    button[data-testid] span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

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
        0%, 100% { opacity: 0.35; transform: scale(0.97); }
        50%       { opacity: 1;    transform: scale(1); }
    }
    @keyframes shimmer {
        0%   { background-position: -400% center; }
        100% { background-position:  400% center; }
    }

    /* ── Sidebar nav buttons ───────────────────────────────────── */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #a1a1aa !important;
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
        background: rgba(245, 158, 11, 0.08) !important;
        color: #fafafa !important;
        box-shadow: none !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:focus-visible {
        outline: 2px solid #f59e0b !important;
        outline-offset: 2px !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(245, 158, 11, 0.12) !important;
        color: #f59e0b !important;
        font-weight: 600 !important;
        border-left: 3px solid #f59e0b !important;
        border-radius: 0 8px 8px 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        border: none !important; background: transparent !important; padding: 0.25rem 0 !important;
    }

    /* ── Metric cards ──────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(145deg, #1c1c1f 0%, #18181b 100%);
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
    .metric-card.blue   { border-top-color: #f59e0b; }
    .metric-card.green  { border-top-color: #3fb950; }
    .metric-card.orange { border-top-color: #d29922; }
    .metric-card.red    { border-top-color: #f85149; }
    .metric-label {
        font-size: 0.78rem; color: #a1a1aa; margin-bottom: 0.45rem;
        text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem; font-weight: 800; color: #fafafa; line-height: 1.1;
    }
    .metric-delta { font-size: 0.78rem; margin-top: 0.45rem; color: #a1a1aa; }
    .metric-delta.blue   { color: #f59e0b; }
    .metric-delta.green  { color: #3fb950; }
    .metric-delta.orange { color: #d29922; }
    .metric-delta.red    { color: #f85149; }

    /* ── Scan success banner ───────────────────────────────────── */
    .scan-success-banner {
        display: flex; align-items: center; gap: 1rem;
        background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25);
        border-radius: 10px; padding: 0.85rem 1.25rem; margin-bottom: 1.5rem;
        animation: fadeInUp 0.35s ease both;
    }
    .scan-success-icon { font-size: 1.3rem; color: #22c55e; flex-shrink: 0; }
    .scan-success-text { flex: 1; color: #fafafa; font-size: 0.9rem; }
    .scan-success-text strong { color: #22c55e; }
    .scan-success-score { font-size: 1rem; font-weight: 700; white-space: nowrap; }

    /* ── Score hero card ───────────────────────────────────────── */
    .score-hero-card {
        background: linear-gradient(145deg, #1c1c1f 0%, #18181b 100%);
        border: 1px solid #3f3f46; border-radius: 16px;
        padding: 1.75rem 2rem; margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 2.5rem; flex-wrap: wrap;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        animation: fadeInUp 0.4s ease both;
    }
    .score-hero-left { display: flex; flex-direction: column; align-items: center; min-width: 90px; }
    .score-hero-number { font-size: 4rem; font-weight: 900; line-height: 1; }
    .score-hero-max    { font-size: 0.85rem; color: #a1a1aa; margin-top: 0.1rem; }
    .score-hero-center { display: flex; flex-direction: column; gap: 0.4rem; }
    .score-hero-grade  { font-size: 2.4rem; font-weight: 900; line-height: 1; }
    .score-hero-badge  {
        display: inline-block; padding: 0.28rem 0.8rem;
        border-radius: 20px; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.07em; text-transform: uppercase;
        background: rgba(255,255,255,0.07); color: #d4d4d8;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .score-hero-right { margin-left: auto; }
    .score-hero-meta   { color: #a1a1aa; font-size: 0.82rem; line-height: 2; }
    .score-hero-meta span { color: #fafafa; font-weight: 500; }

    /* ── Category progress bars ────────────────────────────────── */
    .progress-bar-track {
        background: #27272a; border-radius: 4px; height: 6px;
        margin-top: 0.8rem; overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 4px;
        transition: width 0.5s ease;
    }
    .category-status {
        display: inline-block; margin-top: 0.5rem;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em;
        text-transform: uppercase; color: #a1a1aa;
    }
    .category-status.pass { color: #3fb950; }
    .category-status.issues { color: #f85149; }
    .category-reason {
        margin-top: 0.45rem; font-size: 0.75rem; color: #a1a1aa;
        line-height: 1.4; word-break: break-word;
    }

    /* ── Action cards v2 (integrated card + CTA) ──────────────── */
    .actions-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        margin-bottom: 0.5rem;
    }
    .action-card-v2 {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        background: linear-gradient(145deg, #1c1c1f 0%, #18181b 100%);
        border: 1px solid #3f3f46;
        border-radius: 16px;
        padding: 1.6rem;
        text-decoration: none !important;
        cursor: pointer;
        transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .action-card-v2::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top left, rgba(245,158,11,0.04) 0%, transparent 60%);
        pointer-events: none;
    }
    .action-card-v2:hover {
        border-color: rgba(245,158,11,0.38);
        transform: translateY(-4px);
        box-shadow: 0 18px 44px rgba(0,0,0,0.5);
        text-decoration: none !important;
    }
    .action-card-v2:focus-visible {
        outline: 2px solid #f59e0b;
        outline-offset: 3px;
    }
    .action-card-icon-wrap {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .action-card-icon-wrap.amber { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.28); }
    .action-card-icon-wrap.blue  { background: rgba(88,166,255,0.10);  border: 1px solid rgba(88,166,255,0.25); }
    .action-card-icon-wrap.green { background: rgba(63,185,80,0.10);   border: 1px solid rgba(63,185,80,0.25);  }
    .action-card-body { flex: 1; }
    .action-card-title {
        font-size: 1rem; font-weight: 700; color: #fafafa;
        margin: 0 0 0.4rem; letter-spacing: -0.01em;
    }
    .action-card-desc {
        font-size: 0.82rem; color: #71717a; line-height: 1.65; margin: 0;
    }
    .action-cta-btn {
        display: inline-flex; align-items: center;
        font-size: 0.82rem; font-weight: 700;
        padding: 0.55rem 1.1rem; border-radius: 8px;
        letter-spacing: 0.01em;
        align-self: flex-start;
        transition: opacity 0.15s, transform 0.15s;
    }
    .action-cta-btn.primary {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #111113 !important;
    }
    .action-cta-btn.blue-btn {
        background: rgba(88,166,255,0.12);
        border: 1px solid rgba(88,166,255,0.3);
        color: #58a6ff !important;
    }
    .action-cta-btn.green-btn {
        background: rgba(63,185,80,0.10);
        border: 1px solid rgba(63,185,80,0.3);
        color: #3fb950 !important;
    }
    .action-card-v2:hover .action-cta-btn {
        opacity: 0.9;
        transform: translateX(3px);
    }
    @media (max-width: 900px) {
        .actions-grid { grid-template-columns: 1fr; }
    }

    /* ── Main-area primary button: amber theme override ─────────── */
    [data-testid="stMain"] .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #f59e0b, #d97706) !important;
        color: #111113 !important;
        border: none !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stMain"] .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(245,158,11,0.45) !important;
        background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
    }
    [data-testid="stMain"] .stButton > button:focus-visible,
    button[data-testid="baseButton-primary"]:focus-visible,
    button[data-testid="baseButton-secondary"]:focus-visible {
        outline: 2px solid #f59e0b !important;
        outline-offset: 2px !important;
    }

    /* ── Hero Section ──────────────────────────────────────────── */
    .hero-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        padding: 5rem 3.5rem;
        background: linear-gradient(135deg, #090911 0%, #0d0f1c 60%, #070810 100%);
        border-radius: 20px;
        border: 1px solid #1c1f35;
        box-shadow: 0 0 80px rgba(245,158,11,0.07), 0 24px 70px rgba(0,0,0,0.6);
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
        background-image: radial-gradient(rgba(245,158,11,0.08) 1px, transparent 1px);
        background-size: 30px 30px;
        pointer-events: none;
        border-radius: inherit;
    }
    /* Amber glow top-right */
    .hero-glow-top {
        position: absolute; top: -120px; right: -120px;
        width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(245,158,11,0.09) 0%, transparent 65%);
        pointer-events: none;
    }
    /* Warm glow bottom-left */
    .hero-glow-bottom {
        position: absolute; bottom: -100px; left: -100px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(217,119,6,0.07) 0%, transparent 65%);
        pointer-events: none;
    }
    .hero-content { flex: 1; min-width: 320px; max-width: 560px; position: relative; z-index: 1; }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(245,158,11,0.08);
        border: 1px solid rgba(245,158,11,0.28);
        color: #f59e0b;
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
        background: #f59e0b;
        border-radius: 50%;
        animation: pulseDot 2s ease-in-out infinite;
        flex-shrink: 0;
    }
    .hero-title {
        font-size: 3.1rem;
        font-weight: 900;
        line-height: 1.1;
        margin: 0 0 1.1rem;
        background: linear-gradient(135deg, #ffffff 20%, #fde68a 60%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.08rem;
        color: var(--text-2, #8892aa);
        line-height: 1.75;
        margin: 0 0 1.75rem;
        max-width: 480px;
        font-family: var(--font-body, 'DM Sans', sans-serif);
    }
    .hero-pills {
        display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0;
    }
    .hero-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        color: #a1a1aa;
        font-size: 0.78rem;
        padding: 0.26rem 0.75rem;
        border-radius: 20px;
        transition: border-color 0.2s, color 0.2s;
    }
    .hero-pill:hover { border-color: rgba(245,158,11,0.3); color: #d4d4d8; }

    /* ── Hero CTA buttons ──────────────────────────────────────── */
    .hero-cta-row {
        display: flex; gap: 0.85rem; flex-wrap: wrap; margin: 2rem 0 2.5rem;
    }
    .hero-btn-primary {
        display: inline-flex; align-items: center; gap: 0.45rem;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #0a0a0a !important; font-weight: 700; font-size: 0.92rem;
        padding: 0.75rem 1.6rem; border-radius: 10px;
        text-decoration: none !important;
        box-shadow: 0 4px 20px rgba(245,158,11,0.35);
        transition: transform 0.15s, box-shadow 0.15s;
        font-family: var(--font-body, 'DM Sans', sans-serif) !important;
    }
    .hero-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(245,158,11,0.5);
        color: #0a0a0a !important; text-decoration: none !important;
    }
    .hero-btn-secondary {
        display: inline-flex; align-items: center; gap: 0.45rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        color: #e2e8f0 !important; font-weight: 600; font-size: 0.92rem;
        padding: 0.75rem 1.6rem; border-radius: 10px;
        text-decoration: none !important;
        transition: background 0.15s, border-color 0.15s, color 0.15s;
        font-family: var(--font-body, 'DM Sans', sans-serif) !important;
    }
    .hero-btn-secondary:hover {
        background: rgba(245,158,11,0.08);
        border-color: rgba(245,158,11,0.3);
        color: #f8fafc !important; text-decoration: none !important;
    }

    /* ── Hero stats row ─────────────────────────────────────────── */
    .hero-stats {
        display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 0;
    }
    .hero-stat-item { display: flex; flex-direction: column; }
    .hero-stat-num {
        font-size: 1.65rem; font-weight: 800; color: #fafafa; line-height: 1;
    }
    .hero-stat-label {
        font-size: 0.72rem; color: #71717a; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 0.2rem; font-weight: 600;
    }

    /* ── Product mockup card ────────────────────────────────────── */
    .hero-mockup {
        flex-shrink: 0; width: 380px; position: relative; z-index: 1;
    }
    .mockup-window {
        background: #111113;
        border: 1px solid #3f3f46;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 24px 60px rgba(0,0,0,0.7), 0 0 0 1px #27272a;
    }
    .mockup-titlebar {
        background: #18181b;
        padding: 0.65rem 1rem;
        display: flex; align-items: center; gap: 0.5rem;
        border-bottom: 1px solid #27272a;
    }
    .mockup-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .mockup-dot.red    { background: #ff5f57; }
    .mockup-dot.yellow { background: #febc2e; }
    .mockup-dot.green  { background: #28c840; }
    .mockup-url {
        flex: 1; background: #111113; border: 1px solid #3f3f46;
        border-radius: 6px; padding: 0.22rem 0.65rem;
        font-size: 0.72rem; color: #a1a1aa; margin-left: 0.5rem;
    }
    .mockup-body { padding: 1.25rem 1.25rem 1.5rem; }
    .mockup-site-row {
        display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;
    }
    .mockup-favicon {
        width: 20px; height: 20px; border-radius: 4px;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        flex-shrink: 0;
    }
    .mockup-site-name { font-size: 0.78rem; color: #a1a1aa; }
    .mockup-score-row {
        display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;
        padding: 0.85rem 1rem; background: #101012;
        border: 1px solid #27272a; border-radius: 10px;
    }
    .mockup-grade {
        width: 52px; height: 52px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; font-weight: 900; flex-shrink: 0;
        background: rgba(63,185,80,0.12); border: 2px solid #3fb950; color: #3fb950;
    }
    .mockup-score-num { font-size: 1.6rem; font-weight: 800; color: #fafafa; line-height: 1; }
    .mockup-score-sub { font-size: 0.7rem; color: #a1a1aa; margin-top: 0.15rem; }
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
        border-radius: 7px; color: #d4d4d8;
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
        background: radial-gradient(circle, rgba(245,158,11,0.06) 0%, transparent 70%);
        pointer-events: none; border-radius: 50%;
    }

    /* ── Section divider ─────────────────────────────────────────── */
    .hero-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #1c1f35 25%, #1c1f35 75%, transparent 100%);
        margin: 3rem 0;
    }

    /* ── Section eyebrow labels ────────────────────────────────── */
    .section-eyebrow {
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.13em;
        text-transform: uppercase; color: #f59e0b; margin-bottom: 0.15rem;
    }
    .section-heading {
        font-size: 1.35rem; font-weight: 700; color: #fafafa; margin: 0 0 1.1rem;
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
        .section-heading { font-size: 1.1rem; }
        .actions-grid { grid-template-columns: 1fr; }
        .recent-scan-score-wrap { min-width: 72px; }
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
        background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(217,119,6,0.2));
        border: 1px solid rgba(245,158,11,0.28);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
    }
    .sb-name {
        font-size: 0.98rem; font-weight: 700; color: #fafafa; line-height: 1.2;
        letter-spacing: -0.01em;
    }
    .sb-tag {
        font-size: 0.62rem; color: #52525b; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 1px;
    }
    .sb-hr {
        height: 1px; background: #27272a;
        margin: 0.4rem 0 0.75rem;
    }
    .sb-section-label {
        font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: #52525b;
        padding: 0 0.25rem 0.4rem;
        font-family: var(--font-mono, 'JetBrains Mono', monospace);
    }
    .sb-stats-row {
        display: flex; gap: 0; margin: 0.25rem 0 0.75rem;
    }
    .sb-stat {
        flex: 1; text-align: center; padding: 0.65rem 0.25rem;
        background: #111113; border-radius: 8px; margin: 0 0.2rem;
    }
    .sb-stat-val {
        font-size: 1.2rem; font-weight: 800; color: #fafafa; line-height: 1;
    }
    .sb-stat-label {
        font-size: 0.6rem; color: #52525b; text-transform: uppercase;
        letter-spacing: 0.07em; margin-top: 3px;
    }
    .sb-footer {
        text-align: center; font-size: 0.62rem; color: #3f3f46;
        padding: 0.5rem 0 0.25rem;
    }

    /* ── Empty state ───────────────────────────────────────────── */
    .empty-state {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; text-align: center;
        padding: 3.5rem 2rem; gap: 0.65rem;
        background: linear-gradient(145deg, #141416 0%, #111113 100%);
        border: 1px dashed #3f3f46; border-radius: 16px;
        animation: fadeInUp 0.4s ease both;
    }
    .empty-state-icon { font-size: 3rem; line-height: 1; margin-bottom: 0.25rem; }
    .empty-state-title {
        font-size: 1.05rem; font-weight: 700; color: #d4d4d8; margin: 0;
    }
    .empty-state-body {
        font-size: 0.85rem; color: #52525b; max-width: 340px; line-height: 1.6; margin: 0;
    }

    /* ── Batch status pills ─────────────────────────────────────── */
    .batch-status-row {
        display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0.75rem 0;
    }
    .batch-pill {
        display: inline-flex; align-items: center; gap: 0.35rem;
        font-size: 0.72rem; font-weight: 600; padding: 0.28rem 0.65rem;
        border-radius: 20px; border: 1px solid; white-space: nowrap;
    }
    .batch-pill.queued  { background: rgba(113,113,122,0.08); border-color: rgba(113,113,122,0.2); color: #71717a; }
    .batch-pill.scanning{ background: rgba(245,158,11,0.08);  border-color: rgba(245,158,11,0.3);  color: #f59e0b; }
    .batch-pill.done    { background: rgba(63,185,80,0.08);   border-color: rgba(63,185,80,0.25);  color: #3fb950; }
    .batch-pill.error   { background: rgba(248,81,73,0.08);   border-color: rgba(248,81,73,0.25);  color: #f85149; }
    .batch-pill-dot {
        width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
        background: currentColor;
    }

    /* ── Batch summary bar ──────────────────────────────────────── */
    .batch-summary-bar {
        display: flex; gap: 1.25rem; flex-wrap: wrap;
        background: rgba(12,12,14,0.7); border: 1px solid #27272a;
        border-radius: 12px; padding: 1rem 1.5rem; margin: 1rem 0;
    }
    .batch-summary-item { display: flex; flex-direction: column; gap: 0.1rem; }
    .batch-summary-val  { font-size: 1.5rem; font-weight: 800; line-height: 1; }
    .batch-summary-lbl  { font-size: 0.68rem; color: #52525b; text-transform: uppercase; letter-spacing: 0.07em; }
    .batch-summary-item.success .batch-summary-val { color: #3fb950; }
    .batch-summary-item.warn    .batch-summary-val { color: #d29922; }
    .batch-summary-item.danger  .batch-summary-val { color: #f85149; }
    .batch-summary-item.info    .batch-summary-val { color: #f59e0b; }

    /* ── Sidebar nav badge ──────────────────────────────────────── */
    .sb-nav-badge {
        display: inline-block; margin-left: 0.45rem;
        background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.25);
        color: #f59e0b; font-size: 0.6rem; font-weight: 700;
        padding: 0.1rem 0.42rem; border-radius: 20px;
        vertical-align: middle; line-height: 1.6;
    }

    /* ── Finding cards ──────────────────────────────────────────── */
    .finding-card {
        display: flex; align-items: flex-start; gap: 0.75rem;
        background: rgba(12,12,14,0.5); border: 1px solid #27272a;
        border-radius: 10px; padding: 0.85rem 1rem;
        margin-bottom: 0.6rem; animation: fadeInUp 0.3s ease both;
    }
    .finding-card.pass   { border-left: 3px solid #3fb950; }
    .finding-card.medium { border-left: 3px solid #d29922; }
    .finding-card.high   { border-left: 3px solid #f85149; }
    .finding-card-icon   { font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }
    .finding-card-body   { flex: 1; min-width: 0; }
    .finding-card-title  { font-size: 0.85rem; font-weight: 600; color: #d4d4d8; margin-bottom: 0.2rem; }
    .finding-card-text   { font-size: 0.78rem; color: #a1a1aa; line-height: 1.5; word-break: break-word; }
    .finding-card-badge  {
        font-size: 0.62rem; font-weight: 700; padding: 0.15rem 0.5rem;
        border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em;
        flex-shrink: 0; margin-top: 2px;
    }
    .badge-pass   { background: rgba(63,185,80,0.12);   border: 1px solid rgba(63,185,80,0.3);   color: #3fb950; }
    .badge-medium { background: rgba(210,153,34,0.12);  border: 1px solid rgba(210,153,34,0.3);  color: #d29922; }
    .badge-high   { background: rgba(248,81,73,0.12);   border: 1px solid rgba(248,81,73,0.3);   color: #f85149; }

    /* ── Recommendation list ────────────────────────────────────── */
    .rec-item {
        display: flex; align-items: flex-start; gap: 0.75rem;
        padding: 0.75rem 0; border-bottom: 1px solid #27272a;
    }
    .rec-item:last-child { border-bottom: none; }
    .rec-num {
        min-width: 24px; height: 24px; border-radius: 50%;
        background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);
        color: #f59e0b; font-size: 0.72rem; font-weight: 700;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .rec-text { font-size: 0.84rem; color: #d4d4d8; line-height: 1.6; }

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
        background: rgba(24, 24, 27, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(245, 158, 11, 0.1);
    }
    .score-display-value {
        font-size: 64px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .score-display-max {
        font-size: 14px;
        color: #a1a1aa;
        margin-bottom: 15px;
    }
    .score-display-grade {
        font-size: 24px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .score-display-status {
        font-size: 12px;
        color: #d4d4d8;
    }

    .stats-summary-box {
        background: rgba(24, 24, 27, 0.5);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(245, 158, 11, 0.08);
        font-size: 14px;
    }
    .stats-summary-item {
        margin-bottom: 10px;
    }
    .stats-summary-label {
        color: #a1a1aa;
        display: block;
        margin-bottom: 3px;
    }
    .stats-summary-value {
        color: #d4d4d8;
        word-break: break-all;
    }
    .stats-summary-value.status {
        font-weight: bold;
    }

    .ai-analysis-box {
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        background: rgba(245, 158, 11, 0.02);
        margin: 1.5rem 0;
    }
    .ai-analysis-title {
        color: #f59e0b;
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

    /* ── Action card: fix <a> color inheritance ─────────────── */
    a.action-card-v2,
    a.action-card-v2:hover,
    a.action-card-v2:visited { color: inherit !important; text-decoration: none !important; }
    .action-card-v2 .action-card-title { color: #fafafa !important; }
    .action-card-v2 .action-card-desc  { color: #71717a !important; }

    /* ── Form submit button: amber override ──────────────────── */
    [data-testid="stFormSubmitButton"] > button,
    button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #f59e0b, #d97706) !important;
        color: #111113 !important;
        border: none !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover,
    button[kind="primaryFormSubmit"]:hover {
        background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(245,158,11,0.45) !important;
    }

    /* ── App background: gradient mesh ──────────────────────── */
    [data-testid="stApp"] {
        background:
            radial-gradient(ellipse 900px 700px at 0% 0%, rgba(245,158,11,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 700px 500px at 100% 100%, rgba(124,58,237,0.05) 0%, transparent 55%),
            #090909 !important;
    }

    /* ── Page hero ───────────────────────────────────────────── */
    .page-hero {
        display: flex; align-items: center; gap: 1.25rem;
        padding: 1.5rem 0 2rem;
        border-bottom: 1px solid #27272a;
        margin-bottom: 2rem;
    }
    .page-hero-icon {
        width: 56px; height: 56px; border-radius: 16px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem;
    }
    .page-hero-icon.amber { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3); }
    .page-hero-icon.blue  { background: rgba(88,166,255,0.10);  border: 1px solid rgba(88,166,255,0.28); }
    .page-hero-title {
        font-size: 1.8rem; font-weight: 800; color: #fafafa; margin: 0;
        letter-spacing: -0.025em; line-height: 1.15;
    }
    .page-hero-subtitle {
        font-size: 0.87rem; color: #71717a; margin: 0.3rem 0 0; line-height: 1.5;
    }

    /* ── Scan form card (targets Streamlit form element) ─────── */
    [data-testid="stForm"] {
        background: linear-gradient(145deg, #141416 0%, #111113 100%);
        border: 1px solid #3f3f46 !important;
        border-radius: 16px !important;
        padding: 1.5rem 1.75rem 1.25rem !important;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    [data-testid="stForm"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #f59e0b 0%, rgba(245,158,11,0.25) 60%, transparent 100%);
        pointer-events: none;
    }

    /* ── Scan feature pills (detects row) ────────────────────── */
    .scan-feature-row {
        display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0.5rem 0 1.25rem;
    }
    .scan-feature-pill {
        display: inline-flex; align-items: center; gap: 0.3rem;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        color: #71717a; font-size: 0.74rem; font-weight: 500;
        padding: 0.22rem 0.7rem; border-radius: 20px;
    }

    /* ── AI toggle card ──────────────────────────────────────── */
    .ai-toggle-card {
        background: linear-gradient(145deg, #141416, #111113);
        border: 1px solid #3f3f46; border-radius: 12px;
        padding: 0.75rem 1.25rem; margin: 0 0 1.25rem;
        display: flex; align-items: center; gap: 0.85rem;
    }
    .ai-toggle-badge {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em;
        text-transform: uppercase; color: #f59e0b;
        background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.22);
        padding: 0.18rem 0.55rem; border-radius: 20px; flex-shrink: 0;
    }

    /* ── Batch upload card ───────────────────────────────────── */
    .batch-upload-wrap {
        background: linear-gradient(145deg, #141416, #111113);
        border: 1px solid #3f3f46; border-radius: 16px;
        padding: 1.5rem 1.75rem 1.25rem;
        position: relative; overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        margin-bottom: 1.25rem;
    }
    .batch-upload-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #58a6ff 0%, rgba(88,166,255,0.2) 60%, transparent 100%);
        pointer-events: none;
    }
    .batch-help-row {
        display: flex; flex-wrap: wrap; gap: 1.5rem;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px; padding: 0.85rem 1.1rem;
        margin-top: 0.5rem;
    }
    .batch-help-item {
        display: flex; align-items: flex-start; gap: 0.5rem;
        font-size: 0.78rem; color: #71717a; line-height: 1.5;
    }
    .batch-help-icon { font-size: 0.85rem; flex-shrink: 0; margin-top: 1px; }

    /* ── Recent Scans list ──────────────────────────────────────── */
    .recent-scans-list {
        display: flex; flex-direction: column; gap: 0.6rem;
    }
    .recent-scan-row {
        display: flex; align-items: center; gap: 1.25rem;
        background: linear-gradient(145deg, #1c1c1f, #18181b);
        border: 1px solid #3f3f46; border-radius: 12px;
        padding: 0.9rem 1.2rem;
        transition: border-color 0.2s, transform 0.15s;
    }
    .recent-scan-row:hover {
        border-color: rgba(245,158,11,0.28);
        transform: translateX(3px);
    }
    .recent-scan-url { flex: 1; min-width: 0; }
    .recent-scan-domain {
        font-size: 0.88rem; font-weight: 600; color: #fafafa;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .recent-scan-date { font-size: 0.72rem; color: #52525b; margin-top: 0.15rem; }
    .recent-scan-score-wrap { min-width: 100px; }
    .recent-scan-score-num {
        font-size: 1.1rem; font-weight: 800; color: #fafafa; line-height: 1;
    }
    .recent-scan-score-max { font-size: 0.72rem; color: #52525b; font-weight: 400; }
    .recent-scan-bar-track {
        background: #27272a; border-radius: 4px; height: 4px;
        margin-top: 0.35rem; overflow: hidden; width: 100%;
    }
    .recent-scan-bar-fill { height: 100%; border-radius: 4px; }
    .recent-scan-grade {
        width: 38px; height: 38px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; font-weight: 900; flex-shrink: 0;
    }
    .recent-scan-view-btn {
        font-size: 0.78rem; font-weight: 700; color: #a1a1aa !important;
        background: rgba(255,255,255,0.05); border: 1px solid #3f3f46;
        border-radius: 8px; padding: 0.38rem 0.85rem;
        text-decoration: none !important; flex-shrink: 0;
        transition: color 0.15s, border-color 0.15s, background 0.15s;
    }
    .recent-scan-view-btn:hover {
        color: #f59e0b !important; border-color: rgba(245,158,11,0.35);
        background: rgba(245,158,11,0.07); text-decoration: none !important;
    }

    /* ════════════════════════════════════════════════════════════
       TYPOGRAPHY OVERRIDES — Syne (display) · Mono (data)
       ════════════════════════════════════════════════════════════ */

    /* Display headings → Syne */
    .page-hero-title, .hero-title, .section-heading,
    .action-card-title, .sb-name, .score-hero-grade {
        font-family: var(--font-display) !important;
    }
    .page-hero-title {
        font-size: 2.1rem !important; font-weight: 800 !important;
        letter-spacing: -0.03em !important; line-height: 1.15 !important;
    }
    .hero-title {
        font-size: 3.5rem !important; font-weight: 800 !important;
        letter-spacing: -0.04em !important;
    }
    .section-heading {
        font-size: 1.5rem !important; font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }
    .sb-name { font-weight: 700 !important; letter-spacing: -0.015em !important; }
    .action-card-title {
        font-size: 1.05rem !important; font-weight: 700 !important;
        letter-spacing: -0.015em !important;
    }
    .score-hero-grade { font-weight: 800 !important; }

    /* Data / metrics → JetBrains Mono */
    .metric-value, .metric-label,
    .score-hero-number, .score-hero-max,
    .batch-summary-val, .batch-summary-lbl,
    .recent-scan-score-num, .recent-scan-score-max,
    .rec-num, .scan-feature-pill,
    .sb-stat-val, .sb-stat-label,
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] > div {
        font-family: var(--font-mono) !important;
    }
    .metric-value {
        font-size: 2.7rem !important;
        font-weight: 400 !important;
        letter-spacing: -0.035em !important;
    }
    .metric-label {
        font-size: 0.65rem !important;
        letter-spacing: 0.13em !important;
        color: var(--text-3) !important;
    }
    .score-hero-number {
        font-family: var(--font-mono) !important;
        font-weight: 400 !important;
        letter-spacing: -0.045em !important;
    }
    [data-testid="stMetricLabel"] > div {
        font-size: 0.65rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    /* ════════════════════════════════════════════════════════════
       LAYOUT & SURFACE OVERRIDES
       ════════════════════════════════════════════════════════════ */

    /* App background — stronger gradient mesh */
    [data-testid="stApp"] {
        background:
            radial-gradient(ellipse 1300px 900px at -10% -15%, rgba(245,158,11,0.09) 0%, transparent 52%),
            radial-gradient(ellipse 900px 700px at 115% 115%, rgba(139,92,246,0.07) 0%, transparent 52%),
            radial-gradient(ellipse 600px 400px at 60% 40%, rgba(245,158,11,0.02) 0%, transparent 40%),
            var(--bg) !important;
    }

    /* Sidebar — deeper, more refined */
    [data-testid="stSidebar"] > div:first-child {
        background: #07080e !important;
        border-right: 1px solid #181a2c !important;
    }

    /* Metric cards — darker surface, sharper border, crisper shadow */
    .metric-card {
        background: linear-gradient(145deg, #0e1020 0%, #0a0c17 100%) !important;
        border: 1px solid #1c1f35 !important;
        border-top: 3px solid !important;
        box-shadow: 0 4px 28px rgba(0,0,0,0.5),
                    inset 0 1px 0 rgba(255,255,255,0.025) !important;
    }
    .metric-card:hover {
        box-shadow: 0 16px 40px rgba(0,0,0,0.55),
                    inset 0 1px 0 rgba(255,255,255,0.04) !important;
    }

    /* Score hero card — darker */
    .score-hero-card {
        background: linear-gradient(145deg, #0e1020 0%, #0a0c17 100%) !important;
        border-color: #1c1f35 !important;
    }

    /* Action cards v2 — deeper background */
    .action-card-v2 {
        background: linear-gradient(145deg, #0e1020 0%, #0a0c17 100%) !important;
        border-color: #1c1f35 !important;
    }
    .action-card-v2:hover {
        border-color: rgba(245,158,11,0.42) !important;
        box-shadow: 0 20px 52px rgba(0,0,0,0.55),
                    0 0 0 1px rgba(245,158,11,0.14) !important;
    }

    /* Form card — deeper */
    [data-testid="stForm"] {
        background: linear-gradient(145deg, #0e1020 0%, #0b0d18 100%) !important;
        border-color: #1c1f35 !important;
    }

    /* Recent scan rows */
    .recent-scan-row {
        background: linear-gradient(145deg, #0e1020, #0a0c17) !important;
        border-color: #1c1f35 !important;
    }
    .recent-scan-row:hover { border-color: rgba(245,158,11,0.32) !important; }

    /* Batch upload wrap */
    .batch-upload-wrap {
        background: linear-gradient(145deg, #0e1020 0%, #0b0d18 100%) !important;
        border-color: #1c1f35 !important;
    }

    /* AI toggle card */
    .ai-toggle-card { background: linear-gradient(145deg, #0e1020, #0a0c17) !important; border-color: #1c1f35 !important; }

    /* Empty state */
    .empty-state { background: linear-gradient(145deg, #0e1020 0%, #0a0c17 100%) !important; border-color: #1c1f35 !important; }

    /* Finding cards */
    .finding-card {
        background: rgba(10,12,23,0.7) !important;
        border-color: #1c1f35 !important;
    }
    .finding-card-title { font-weight: 600 !important; letter-spacing: -0.01em !important; }

    /* Page hero — amber accent underline */
    .page-hero { position: relative; }
    .page-hero::after {
        content: '';
        position: absolute; bottom: -1px; left: 0;
        width: 72px; height: 2px;
        background: var(--primary); border-radius: 2px;
    }

    /* Batch help row — darker */
    .batch-help-row {
        background: rgba(255,255,255,0.015) !important;
        border-color: rgba(255,255,255,0.05) !important;
    }

    /* ── Reduced motion ─────────────────────────────────────────── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
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
        </div>
        <div class="sb-hr"></div>
        <div class="sb-section-label">Navigation</div>
        """, unsafe_allow_html=True)

        # ── Fetch stats once for badge + stats row ────────────────
        _sidebar_stats: dict = {}
        try:
            from database.operations import get_scan_statistics
            _sidebar_stats = get_scan_statistics() or {}
        except Exception:
            pass
        _total_scans = _sidebar_stats.get("total_scans", 0)

        NAV_ITEMS = [
            ("dashboard",  "Dashboard",  None),
            ("quick_scan", "Quick Scan", None),
            ("batch_scan", "Batch Scan", None),
            ("history",    "History",    _total_scans if _total_scans else None),
        ]
        for page_id, label, badge in NAV_ITEMS:
            is_active = st.session_state.page == page_id
            display_label = label if not badge else f"{label}  {badge}"
            if st.button(
                display_label,
                key=f"nav_{page_id}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Stats row ─────────────────────────────────────────────
        st.markdown('<div class="sb-hr" style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)
        if _sidebar_stats:
            total = _sidebar_stats.get("total_scans", 0)
            avg = _sidebar_stats.get("avg_score", 0)
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

        # ── Footer ────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-footer">GDPR &amp; CCPA Scanner</div>',
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
