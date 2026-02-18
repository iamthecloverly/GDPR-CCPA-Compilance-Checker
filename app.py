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

# Modern dark theme styling - COMPLETE
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stApp"] {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 50%, #16213e 100%) !important;
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    [data-testid="stAppViewContainer"] {
        background: transparent;
    }
    
    [data-testid="stHeader"] {
        background: rgba(20, 23, 36, 0.7);
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(20, 23, 36, 0.95) 100%) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: #e0e7ff !important;
    }
    
    .stMainBlockContainer {
        background: transparent;
        padding: 2rem 1rem;
    }
    
    h1 { 
        color: #e0e7ff !important;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    h2, h3, h4, h5, h6 { 
        color: #e0e7ff !important;
        font-weight: 600;
    }
    
    p, div, span, label { 
        color: #c7d2fe !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.2)) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        color: #e0e7ff !important;
        font-weight: 500;
        transition: all 0.3s ease;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.5), rgba(139, 92, 246, 0.3)) !important;
        border-color: rgba(139, 92, 246, 0.6) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 33, 46, 0.5);
        border-bottom: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 8px;
        padding: 0 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #a1aec0 !important;
        border-radius: 6px 6px 0 0;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2);
        color: #e0e7ff !important;
        border-bottom: 2px solid rgba(99, 102, 241, 0.6);
    }
    
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 8px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        background: rgba(30, 33, 46, 0.6) !important;
    }
    
    .stExpanderDetails {
        background: rgba(30, 33, 46, 0.4);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    .metric-value {
        color: #60a5fa !important;
        font-weight: 600;
    }
    
    input, textarea, select {
        background: rgba(30, 33, 46, 0.8) !important;
        color: #e0e7ff !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: rgba(99, 102, 241, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a1aec0 !important;
    }
    
    .dataframe {
        background: rgba(20, 23, 36, 0.5) !important;
        color: #e0e7ff;
    }
    
    .dataframe th {
        background: rgba(30, 33, 46, 0.8) !important;
        color: #e0e7ff !important;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3) !important;
    }
    
    .dataframe td {
        border-color: rgba(99, 102, 241, 0.1) !important;
        color: #c7d2fe !important;
    }
    
    a {
        color: #60a5fa !important;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: #93c5fd !important;
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
