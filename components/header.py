"""Header and metric card components."""

import streamlit as st
from typing import Dict, Any


def create_metric_card(title: str, value: str, delta: str, color: str):
    """
    Create a custom metric card with colored border.

    Args:
        title: Metric title/label
        value: Main metric value to display
        delta: Delta text (e.g., "+12 this week")
        color: Color theme - 'blue', 'orange', 'green', or 'red'
    """
    html_code = f"""
    <div class="metric-card {color}">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta {color}">{delta}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)


def render_stats_row(stats: Dict[str, Any]):
    """
    Render a row of stat cards using native Streamlit metrics.

    Args:
        stats: Dictionary containing statistics
               - total_scans: int
               - avg_score: float
               - compliant_count: int
               - at_risk_count: int
    """
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        total = stats.get("total_scans", 0)
        st.metric(
            "Total Scans",
            f"{total:,}",
            delta="All time" if total > 0 else None,
            delta_color="off"
        )

    with col2:
        avg_score = stats.get("avg_score", 0)
        baseline = 70
        delta_val = avg_score - baseline
        delta_text = f"{delta_val:+.0f} vs baseline" if avg_score > 0 else None

        st.metric(
            "Average Score",
            f"{avg_score:.0f}/100",
            delta=delta_text,
            delta_color="normal" if delta_val >= 0 else "inverse"
        )

    with col3:
        compliant = stats.get("compliant_count", 0)
        st.metric(
            "Compliant",
            f"{compliant:,}",
            delta="Grade A" if compliant > 0 else None,
            delta_color="off"
        )

    with col4:
        at_risk = stats.get("at_risk_count", 0)
        st.metric(
            "At Risk",
            f"{at_risk:,}",
            delta="High Priority" if at_risk > 0 else None,
            delta_color="inverse" if at_risk > 0 else "off"
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
