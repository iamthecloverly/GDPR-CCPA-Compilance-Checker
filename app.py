"""
GDPR/CCPA Compliance Checker - Main Application

A comprehensive tool for checking website compliance with GDPR and CCPA regulations.
This is the main entry point that routes to different pages.
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
from pages.dashboard import render_dashboard_page as dashboard_page
from pages.quick_scan import render_quick_scan_page as quick_scan_page
from pages.batch_scan import render_batch_scan_page as batch_scan_page
from pages.history import render_history_page as history_page
from pages.settings import render_settings_page as settings_page

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="GDPR/CCPA Compliance Checker",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal Clean Theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stApp"] {
        background: #f8f9fa !important;
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: #f8f9fa;
    }
    
    [data-testid="stHeader"] {
        background: #ffffff;
        border-bottom: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: #374151 !important;
    }
    
    .stMainBlockContainer {
        background: transparent;
        padding: 2rem 2rem;
    }
    
    h1 { 
        color: #1f2937 !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    h2 { 
        color: #2c3e50 !important;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    h3, h4, h5, h6 { 
        color: #374151 !important;
        font-weight: 600;
    }
    
    p, div, span, label { 
        color: #4b5563 !important;
        line-height: 1.5;
    }
    
    .stButton > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        font-weight: 500;
        transition: all 0.2s ease;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        background: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button[kind="secondary"] {
        background: #e5e7eb !important;
        color: #374151 !important;
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #d1d5db !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #6b7280 !important;
        border-radius: 0;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent;
        color: #3b82f6 !important;
        border-bottom: 3px solid #3b82f6;
    }
    
    .stInfo {
        background: #f0f7ff !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 6px;
    }
    
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #b7e4c7 !important;
        border-radius: 6px;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fde68a !important;
        border-radius: 6px;
    }
    
    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        border-radius: 6px;
    }
    
    .stExpanderDetails {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 1rem;
    }
    
    .metric-value {
        color: #3b82f6 !important;
        font-weight: 700;
        font-size: 1.5em;
    }
    
    input, textarea, select {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px;
        padding: 0.5rem 0.75rem !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none;
    }
    
    [data-testid="stMetricValue"] {
        color: #3b82f6 !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6b7280 !important;
    }
    
    .dataframe {
        background: #ffffff !important;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #f9fafb !important;
        color: #1f2937 !important;
        border-bottom: 2px solid #e5e7eb !important;
        font-weight: 600;
    }
    
    .dataframe td {
        border-color: #e5e7eb !important;
        color: #4b5563 !important;
    }
    
    .dataframe tr:hover {
        background: #f9fafb !important;
    }
    
    a {
        color: #3b82f6 !important;
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: #2563eb !important;
        text-decoration: underline;
    }
    
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "page" not in st.session_state or st.session_state.page not in [
    "dashboard", "quick_scan", "batch_scan", "history", "settings"
]:
    st.session_state.page = "dashboard"


def render_sidebar():
    """Render navigation sidebar with modern UI."""
    with st.sidebar:
        st.markdown("")
        st.markdown("### 🔒 GDPR/CCPA Checker")
        st.markdown("---")
        
        # Navigation buttons
        pages = {
            "dashboard": ("📊 Dashboard", "Overview & Stats"),
            "quick_scan": ("📱 Quick Scan", "Single URL"),
            "batch_scan": ("📦 Batch Scan", "Multiple URLs"),
            "history": ("📜 History", "Past Scans"),
            "settings": ("⚙️ Settings", "Configuration"),
        }
        
        for page_id, (icon_title, description) in pages.items():
            is_active = st.session_state.page == page_id
            
            if st.sidebar.button(
                f"{icon_title}\n_{description}_",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page = page_id
                st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ About")
        st.sidebar.markdown(
            """
            **Version:** 1.0.0
            
            **Features:**
            - Single & batch scanning
            - Real-time analysis
            - Result export (CSV/JSON)
            - Scan caching (24h)
            - Detailed recommendations
            """
        )


def main():
    """Main application router with error handling."""
    try:
        # Render sidebar
        render_sidebar()
        
        # Render appropriate page
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "quick_scan":
            quick_scan_page()
        elif st.session_state.page == "batch_scan":
            batch_scan_page()
        elif st.session_state.page == "history":
            history_page()
        elif st.session_state.page == "settings":
            settings_page()
        else:
            st.error(f"Unknown page: {st.session_state.page}")
            st.session_state.page = "dashboard"
            st.rerun()
    
    except Exception as e:
        logger.error(f"Error rendering page {st.session_state.page}: {e}", exc_info=True)
        st.error(
            f"""
            ### ⚠️ Error Occurred
            
            **Page:** {st.session_state.page}
            **Error:** {str(e)}
            
            Please try refreshing the page or return to the Dashboard.
            """
        )
        if st.button("🔄 Return to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()


if __name__ == "__main__":
    main()
