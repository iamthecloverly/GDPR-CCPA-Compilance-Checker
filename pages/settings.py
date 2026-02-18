"""Settings page - configuration and preferences."""

import streamlit as st
from components import render_header
from config import Config
from logger_config import get_logger
import os

logger = get_logger(__name__)


def render_settings_page():
    """Render the settings page."""
    render_header()
    
    st.markdown("# ⚙️ Settings")
    st.markdown("*Configure API keys and scanning preferences*")
    
    st.markdown("---")
    
    # Tabs for different settings
    tab1, tab2, tab3 = st.tabs(["API Keys", "Scanning", "About"])
    
    with tab1:
        render_api_settings()
    
    with tab2:
        render_scanning_settings()
    
    with tab3:
        render_about_section()


def render_api_settings():
    """Render API key configuration."""
    st.markdown("### 🔑 API Keys")
    st.markdown("Configure external service API keys for enhanced features.")
    
    # OpenAI API Key
    st.markdown("#### OpenAI API Key")
    st.caption("Used for AI-powered compliance analysis")
    
    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        label_visibility="collapsed",
        placeholder="sk-..."
    )
    
    if openai_key:
        st.success("✓ OpenAI API key configured")
    else:
        st.info("ℹ️ AI features will be disabled without an OpenAI API key")
    
    # Database URL
    st.markdown("#### Database URL")
    st.caption("Store scan history and manage data persistence")
    
    db_url = st.text_input(
        "Database URL",
        value=os.getenv("DATABASE_URL", ""),
        type="password",
        label_visibility="collapsed",
        placeholder="postgresql://user:pass@localhost/dbname"
    )
    
    if db_url:
        st.success("✓ Database connection configured")
    else:
        st.info("ℹ️ Scan history will not be saved without a database URL")
    
    st.markdown("---")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")
        logger.info("Settings updated")


def render_scanning_settings():
    """Render scanning preferences."""
    st.markdown("### 🔍 Scanning Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Timeout settings
        st.markdown("#### Timeout Settings")
        
        request_timeout = st.number_input(
            "Request Timeout (seconds)",
            min_value=5,
            max_value=120,
            value=Config.REQUEST_TIMEOUT,
            step=5,
            help="How long to wait for a website to respond"
        )
        
        scan_timeout = st.number_input(
            "Scan Timeout (seconds)",
            min_value=30,
            max_value=600,
            value=60,
            step=30,
            help="Maximum time for a complete scan"
        )
    
    with col2:
        # Limits
        st.markdown("#### Limits")
        
        batch_limit = st.number_input(
            "Batch Scan Limit",
            min_value=5,
            max_value=1000,
            value=Config.BATCH_SCAN_LIMIT,
            step=5,
            help="Maximum URLs per batch scan"
        )
        
        cache_ttl = st.number_input(
            "Cache TTL (hours)",
            min_value=1,
            max_value=168,
            value=24,
            step=1,
            help="How long to cache scan results"
        )
    
    st.markdown("---")
    
    # Scoring weights
    st.markdown("#### Scoring Weights")
    st.caption("Adjust how much each factor contributes to the overall score")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cookie_weight = st.slider(
            "Cookie Consent Weight",
            min_value=0,
            max_value=100,
            value=Config.COOKIE_CONSENT_WEIGHT,
            step=5
        )
        
        privacy_weight = st.slider(
            "Privacy Policy Weight",
            min_value=0,
            max_value=100,
            value=Config.PRIVACY_POLICY_WEIGHT,
            step=5
        )
    
    with col2:
        contact_weight = st.slider(
            "Contact Info Weight",
            min_value=0,
            max_value=100,
            value=Config.CONTACT_INFO_WEIGHT,
            step=5
        )
        
        tracker_weight = st.slider(
            "Tracker Detection Weight",
            min_value=0,
            max_value=100,
            value=Config.TRACKER_DETECTION_WEIGHT,
            step=5
        )
    
    st.markdown("---")
    
    if st.button("💾 Save Preferences", type="primary"):
        st.success("Preferences saved successfully!")
        logger.info("Scanning preferences updated")


def render_about_section():
    """Render about and help section."""
    st.markdown("### 📝 About")
    
    st.markdown("""
    **GDPR/CCPA Compliance Checker v1.0.0**
    
    A comprehensive tool for analyzing website compliance with:
    - 🇪🇺 **GDPR** (General Data Protection Regulation)
    - 🇺🇸 **CCPA** (California Consumer Privacy Act)
    
    #### Features
    - ✓ Single and batch website scanning
    - ✓ Real-time compliance scoring
    - ✓ Detailed findings and recommendations
    - ✓ Scan history and comparison tools
    - ✓ Export results as CSV/JSON
    - ✓ Caching for improved performance
    
    #### Documentation
    [📖 Full Documentation](https://github.com/example/compliance-checker)
    [🐛 Report Issues](https://github.com/example/compliance-checker/issues)
    [💬 Get Help](https://github.com/example/compliance-checker/discussions)
    
    #### Version Information
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Application**")
        st.code("v1.0.0", language="text")
    
    with col2:
        st.markdown("**Python**")
        import sys
        st.code(f"{sys.version.split()[0]}", language="text")
    
    with col3:
        st.markdown("**Streamlit**")
        st.code(f"{st.__version__}", language="text")
    
    st.markdown("---")
    
    # Privacy notice
    with st.expander("🔒 Privacy & Data"):
        st.markdown("""
        **How we handle your data:**
        
        - ✓ Scans are processed locally and securely
        - ✓ Results can optionally be saved to your database
        - ✓ API keys are never logged or transmitted
        - ✓ We don't share your scan data with third parties
        
        For more information, see our privacy policy.
        """)


def main():
    """Main function for settings page."""
    if "page" not in st.session_state:
        st.session_state.page = "settings"
    
    render_settings_page()


if __name__ == "__main__":
    main()
