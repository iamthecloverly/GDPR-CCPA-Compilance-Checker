"""
GDPR/CCPA Compliance Checker - Modern Professional Interface

A production-ready privacy compliance scanner with AI-powered analysis,
real-time scanning, and comprehensive reporting capabilities.
"""

import streamlit as st
import os
import logging
import sys

# Setup base path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and logger
from config import Config
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
    initial_sidebar_state="collapsed"
)

# ============================================================================
# MODERN DARK THEME - SUPERMEMORY INSPIRED
# ============================================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ===== Dark Theme Colors ===== */
    :root {
        --primary: #00d9ff;
        --primary-dark: #00b8d4;
        --primary-light: #4df9ff;
        
        --bg-dark: #0a0e27;
        --bg-darker: #050810;
        --bg-surface: #1a1f3a;
        --bg-surface-light: #252d4a;
        
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #06b6d4;
        
        --text-primary: #f5f7fa;
        --text-secondary: #b4bcd4;
        --text-tertiary: #7a849e;
        
        --border-color: #2a3250;
        --border-light: #3a4260;
    }
    
    /* ===== Base Styles ===== */
    html, body, [data-testid="stApp"] {
        background: #0a0e27 !important;
        background-image: radial-gradient(circle at 20% 50%, rgba(0, 217, 255, 0.03) 0%, transparent 50%),
                          radial-gradient(circle at 80% 80%, rgba(0, 217, 255, 0.02) 0%, transparent 50%);
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    /* ===== Header ===== */
    [data-testid="stHeader"] {
        background: rgba(10, 14, 39, 0.8) !important;
        border-bottom: 1px solid var(--border-color);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* ===== Sidebar (Hidden) ===== */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* ===== Main Content ===== */
    .stMainBlockContainer {
        background: transparent !important;
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Container for pages */
    .main .block-container {
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }
    }
    
    /* ===== Typography ===== */
    h1 {
        color: var(--text-primary) !important;
        font-weight: 700;
        font-size: 42px;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        line-height: 1.2;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-weight: 700;
        font-size: 32px;
        letter-spacing: -0.015em;
        margin-top: 32px;
        margin-bottom: 16px;
        line-height: 1.3;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
        font-size: 24px;
        margin-top: 24px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    
    p, div, span, label {
        color: var(--text-secondary) !important;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* ===== Buttons ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 600;
        font-size: 14px;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 217, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 217, 255, 0.5);
    }
    
    .stButton > button[kind="secondary"] {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-surface-light) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid var(--border-color) !important;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--text-tertiary) !important;
        border-radius: 0 !important;
        font-weight: 500;
        font-size: 14px;
        padding: 12px 16px !important;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent !important;
        color: var(--primary) !important;
        border: none !important;
    }
    
    /* ===== Alerts & Messages ===== */
    .stAlert {
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        padding: 16px !important;
        margin-bottom: 16px;
        background: var(--bg-surface) !important;
        backdrop-filter: blur(10px);
    }
    
    .stInfo {
        background: rgba(6, 182, 212, 0.1) !important;
        border-color: rgba(0, 217, 255, 0.3) !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-color: rgba(16, 185, 129, 0.3) !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-color: rgba(245, 158, 11, 0.3) !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
    }
    
    /* ===== Forms & Inputs ===== */
    input, textarea, select {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        font-family: inherit !important;
        transition: all 0.2s ease;
    }
    
    input:hover, textarea:hover, select:hover {
        border-color: var(--primary) !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: var(--primary) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.15) !important;
        background: var(--bg-surface-light) !important;
    }
    
    input::placeholder {
        color: var(--text-tertiary) !important;
    }
    
    /* ===== Cards & Containers ===== */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(37, 45, 74, 0.5), rgba(26, 31, 58, 0.5)) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 700;
        font-size: 28px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    
    /* ===== Data Tables ===== */
    .dataframe {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .dataframe th {
        background: rgba(0, 217, 255, 0.1) !important;
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--border-light) !important;
        font-weight: 600;
        font-size: 13px;
        padding: 12px !important;
        text-align: left;
    }
    
    .dataframe td {
        border-color: var(--border-color) !important;
        color: var(--text-secondary) !important;
        padding: 12px !important;
        font-size: 14px;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(0, 217, 255, 0.05) !important;
    }
    
    /* ===== Links ===== */
    a {
        color: var(--primary) !important;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: var(--primary-light) !important;
        text-decoration: underline;
    }
    
    /* ===== Code ===== */
    code {
        background: var(--bg-surface) !important;
        color: var(--primary) !important;
        border-radius: 4px;
        border: 1px solid var(--border-color);
        padding: 2px 6px;
        font-family: 'Geist Mono', monospace;
        font-size: 13px;
    }
    
    /* ===== Expander ===== */
    .stExpander {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        overflow: hidden;
        background: var(--bg-surface) !important;
    }
    
    .stExpander > div:first-child {
        background: var(--bg-surface-light) !important;
        padding: 16px !important;
    }
    
    .stExpanderDetails {
        background: var(--bg-surface) !important;
        border-top: 1px solid var(--border-color) !important;
        padding: 16px !important;
    }
    
    /* ===== Divider ===== */
    hr {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 24px 0;
    }
    
    /* ===== Helper Classes ===== */
    .glass-card {
        background: rgba(37, 45, 74, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .glass-card:hover {
        background: rgba(37, 45, 74, 0.5);
        box-shadow: 0 12px 48px rgba(0, 217, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        line-height: 1;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    .badge-error {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .badge-info {
        background: rgba(0, 217, 255, 0.2);
        color: var(--primary);
        border: 1px solid rgba(0, 217, 255, 0.4);
    }
    
    /* ===== Animations ===== */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# APPLICATION STATE & NAVIGATION
# ============================================================================

if "page" not in st.session_state or st.session_state.page not in [
    "dashboard", "quick_scan", "batch_scan", "history"
]:
    st.session_state.page = "dashboard"


def render_top_navigation():
    """Render modern top navigation bar."""
    # Navigation container
    nav_col1, nav_col2 = st.columns([2, 8])
    
    with nav_col1:
        st.markdown(
            """
            <div style="padding: 16px 0;">
                <h2 style="margin: 0; color: var(--primary); font-weight: 700; font-size: 24px;">
                    Privacy Compliance Scanner
                </h2>
                <p style="margin: 0; color: var(--text-tertiary); font-size: 13px;">GDPR & CCPA Analysis</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with nav_col2:
        # Navigation tabs
        pages = [
            ("dashboard", "Dashboard"),
            ("quick_scan", "Quick Scan"),
            ("batch_scan", "Batch Scan"),
            ("history", "History"),
        ]
        
        nav_cols = st.columns(len(pages))
        
        for idx, (page_id, title) in enumerate(pages):
            with nav_cols[idx]:
                is_active = st.session_state.page == page_id
                
                if is_active:
                    st.markdown(
                        f"""
                        <div style="
                            text-align: center; 
                            padding: 16px 12px; 
                            background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(0, 217, 255, 0.05));
                            border-bottom: 3px solid var(--primary);
                            border-radius: 8px 8px 0 0;
                            cursor: pointer;
                        ">
                            <span style="color: var(--primary); font-weight: 600; font-size: 14px;">{title}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(title, key=f"nav_{page_id}", use_container_width=True, type="secondary"):
                        st.session_state.page = page_id
                        st.rerun()
    
    st.markdown("<hr style='margin: 0 0 24px 0; border-color: var(--border-color);' />", unsafe_allow_html=True)


def main():
    """Main application router with error handling."""
    try:
        # Render top navigation
        render_top_navigation()
        
        # Render appropriate page
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
    
    except Exception as e:
        logger.error(f"Error rendering page {st.session_state.page}: {e}", exc_info=True)
        
        # Error UI
        st.error(
            f"""
            ### ⚠️ An Error Occurred
            
            We encountered an issue while rendering this page.
            **Error:** {str(e)}
            
            Please try refreshing the page or navigating to the Dashboard.
            """
        )
        
        if st.button("🔄 Return to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()


if __name__ == "__main__":
    main()
