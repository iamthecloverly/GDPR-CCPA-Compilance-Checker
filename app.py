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
    initial_sidebar_state="expanded"
)

# ============================================================================
# MODERN DESIGN SYSTEM - GLASSMORPHISM + MINIMALIST
# ============================================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ===== Colors - Vibrant Modern Palette ===== */
    :root {
        --color-primary: #8b5cf6;
        --color-primary-dark: #7c3aed;
        --color-primary-light: #a78bfa;
        
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #ef4444;
        --color-info: #0ea5e9;
        
        --color-bg: #ffffff;
        --color-bg-secondary: #f8fafc;
        --color-bg-tertiary: #f1f5f9;
        
        --color-border: #e2e8f0;
        --color-border-light: #f1f5f9;
        
        --color-text-primary: #0f172a;
        --color-text-secondary: #475569;
        --color-text-tertiary: #64748b;
        
        --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
        --shadow-md: 0 4px 6px rgba(15, 23, 42, 0.07), 0 2px 4px rgba(15, 23, 42, 0.05);
        --shadow-lg: 0 10px 15px rgba(15, 23, 42, 0.1), 0 4px 6px rgba(15, 23, 42, 0.05);
        --shadow-xl: 0 20px 25px rgba(15, 23, 42, 0.15), 0 10px 10px rgba(15, 23, 42, 0.05);
        
        --shadow-glass: 0 8px 32px rgba(31, 38, 135, 0.1);
        --shadow-glass-inset: inset 0 0 0 0.5px rgba(255, 255, 255, 0.3);
    }
    
    /* ===== Base Styles ===== */
    html, body, [data-testid="stApp"] {
        background: linear-gradient(135deg, #fafffe 0%, #f5f3ff 50%, #ffe5f0 100%) !important;
        background-attachment: fixed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--color-text-primary);
        line-height: 1.6;
    }
    
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    /* ===== Header ===== */
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-bottom: 1px solid var(--color-border);
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid var(--color-border);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: var(--color-text-primary) !important;
    }
    
    /* ===== Main Content ===== */
    .stMainBlockContainer {
        background: transparent !important;
        padding: 32px 24px;
        max-width: 1400px;
    }
    
    /* ===== Typography ===== */
    h1 {
        color: var(--color-text-primary) !important;
        font-weight: 700;
        font-size: 42px;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    
    h2 {
        color: var(--color-text-primary) !important;
        font-weight: 700;
        font-size: 32px;
        letter-spacing: -0.015em;
        margin-top: 32px;
        margin-bottom: 16px;
        line-height: 1.3;
    }
    
    h3 {
        color: var(--color-text-primary) !important;
        font-weight: 600;
        font-size: 24px;
        margin-top: 24px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    h4, h5, h6 {
        color: var(--color-text-primary) !important;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    
    p, div, span, label {
        color: var(--color-text-secondary) !important;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* ===== Buttons ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600;
        font-size: 14px;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        box-shadow: var(--shadow-md);
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--color-primary-dark) 0%, #0a7ea4 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button[kind="secondary"] {
        background: var(--color-bg-secondary) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--color-bg-tertiary) !important;
        border-color: var(--color-primary) !important;
        color: var(--color-primary) !important;
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid var(--color-border) !important;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--color-text-secondary) !important;
        border-radius: 0 !important;
        font-weight: 500;
        font-size: 14px;
        padding: 12px 16px !important;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-primary) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent !important;
        color: var(--color-primary) !important;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--color-primary);
    }
    
    /* ===== Alerts & Messages ===== */
    .stAlert {
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        padding: 16px !important;
        margin-bottom: 16px;
        box-shadow: var(--shadow-sm);
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.05) !important;
        border-color: rgba(59, 130, 246, 0.2) !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.05) !important;
        border-color: rgba(16, 185, 129, 0.2) !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.05) !important;
        border-color: rgba(245, 158, 11, 0.2) !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.05) !important;
        border-color: rgba(239, 68, 68, 0.2) !important;
    }
    
    .stInfo > div, .stSuccess > div, .stWarning > div, .stError > div {
        color: var(--color-text-primary) !important;
        font-weight: 500;
    }
    
    /* ===== Forms & Inputs ===== */
    input, textarea, select {
        background: var(--color-bg) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        font-family: inherit !important;
        transition: all 0.2s ease;
    }
    
    input:hover, textarea:hover, select:hover {
        border-color: var(--color-primary) !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: var(--color-primary) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1) !important;
    }
    
    input::placeholder {
        color: var(--color-text-tertiary) !important;
    }
    
    /* ===== Sliders ===== */
    .stSlider > div {
        padding: 16px 0;
    }
    
    .stSlider [data-testid="stTickBar"] {
        background-color: var(--color-border) !important;
    }
    
    /* ===== Expandable Sections ===== */
    .stExpander {
        border: 1px solid var(--color-border) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    
    .stExpander > div:first-child {
        background: var(--color-bg-secondary) !important;
        padding: 16px !important;
    }
    
    .stExpanderDetails {
        background: var(--color-bg) !important;
        border-top: 1px solid var(--color-border) !important;
        padding: 16px !important;
    }
    
    /* ===== Metrics ===== */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: var(--shadow-glass);
    }
    
    [data-testid="stMetricValue"] {
        color: var(--color-primary) !important;
        font-weight: 700;
        font-size: 28px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--color-text-secondary) !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--color-text-secondary) !important;
    }
    
    /* ===== Data Tables ===== */
    .dataframe {
        background: var(--color-bg) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 8px !important;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    .dataframe th {
        background: var(--color-bg-secondary) !important;
        color: var(--color-text-primary) !important;
        border-bottom: 2px solid var(--color-border) !important;
        font-weight: 600;
        font-size: 13px;
        padding: 12px !important;
        text-align: left;
    }
    
    .dataframe td {
        border-color: var(--color-border-light) !important;
        color: var(--color-text-secondary) !important;
        padding: 12px !important;
        font-size: 14px;
    }
    
    .dataframe tbody tr:hover {
        background: var(--color-bg-secondary) !important;
    }
    
    /* ===== Links ===== */
    a {
        color: var(--color-primary) !important;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: var(--color-primary-dark) !important;
        text-decoration: underline;
    }
    
    /* ===== Code & Preformatted Text ===== */
    code {
        background: var(--color-bg-secondary) !important;
        color: var(--color-text-primary) !important;
        border-radius: 4px;
        padding: 2px 6px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }
    
    /* ===== Horizontal Line ===== */
    hr {
        border: none;
        border-top: 1px solid var(--color-border);
        margin: 24px 0;
    }
    
    /* ===== Captions & Small Text ===== */
    .caption {
        color: var(--color-text-tertiary) !important;
        font-size: 13px;
        margin-top: 4px;
    }
    
    /* ===== Animations ===== */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slide-up {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* ===== Responsive Design ===== */
    @media (max-width: 768px) {
        h1 {
            font-size: 28px;
        }
        
        h2 {
            font-size: 24px;
        }
        
        .stMainBlockContainer {
            padding: 24px 16px;
        }
        
        [data-testid="metric-container"] {
            padding: 16px !important;
        }
    }
    
    /* ===== Custom Utilities ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 24px;
        box-shadow: var(--shadow-glass);
    }
    
    .glass-card:hover {
        box-shadow: var(--shadow-lg);
        transition: box-shadow 0.3s ease;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        line-height: 1;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.1);
        color: #047857;
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
    }
    
    .badge-error {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
    }
    
    .badge-info {
        background: rgba(59, 130, 246, 0.1);
        color: #0284c7;
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


def render_sidebar():
    """Render modern navigation sidebar."""
    with st.sidebar:
        # Logo & Branding
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("🔒")
        with col2:
            st.markdown("### Privacy Scanner")
        
        st.markdown("*Compliance made simple*")
        st.markdown("---")
        
        # Navigation Menu
        st.markdown("### Navigation")
        
        pages = {
            "dashboard": ("📊", "Dashboard", "Overview and statistics"),
            "quick_scan": ("⚡", "Quick Scan", "Scan single website"),
            "batch_scan": ("📦", "Batch Scan", "Scan multiple URLs"),
            "history": ("📜", "Scan History", "View past scans"),
        }
        
        for page_id, (icon, title, subtitle) in pages.items():
            is_active = st.session_state.page == page_id
            
            if st.button(
                f"{icon} {title}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page = page_id
                st.rerun()
            
            if is_active:
                st.caption(subtitle)
        
        # Footer Info
        st.markdown("---")
        st.markdown("### About")
        st.caption(
            """
            **Version:** 2.0.0
            
            **Features:**
            - AI-powered scanning
            - Real-time analysis
            - Batch processing
            - Compliance scoring
            - Detailed reports
            """
        )


def main():
    """Main application router with error handling."""
    try:
        # Render sidebar
        render_sidebar()
        
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
