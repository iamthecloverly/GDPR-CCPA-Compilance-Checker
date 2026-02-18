"""Header and navigation components."""

import streamlit as st
from typing import Dict, Any


def render_header():
    """Render consistent application header with navigation."""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("### 🔒")
    
    with col2:
        st.markdown("""
        <h1 style="font-size: 28px; margin: 0; color: #e6edf3;">
            GDPR/CCPA Compliance Checker
        </h1>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("⚙️ Settings", key="header_settings"):
            st.session_state.page = "settings"
    
    st.markdown("---")


def render_stats_row(stats: Dict[str, Any]):
    """
    Render a row of stat cards.
    
    Args:
        stats: Dictionary containing statistics
               - total_scans: int
               - avg_score: float
               - compliant_count: int
               - at_risk_count: int
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Scans",
            stats.get("total_scans", 0),
            "scans"
        )
    
    with col2:
        avg_score = stats.get("avg_score", 0)
        st.metric(
            "Avg Score",
            f"{avg_score:.0f}",
            "/ 100"
        )
    
    with col3:
        st.metric(
            "✓ Compliant",
            stats.get("compliant_count", 0),
            "sites"
        )
    
    with col4:
        at_risk = stats.get("at_risk_count", 0)
        st.metric(
            "⚠️ At Risk",
            at_risk,
            "sites"
        )


def render_page_title(title: str, description: str = ""):
    """
    Render a page title with optional description.
    
    Args:
        title: Page title
        description: Optional description text
    """
    st.markdown(f"# {title}")
    if description:
        st.markdown(f"*{description}*")
