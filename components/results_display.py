"""Results display components."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
import altair as alt

# Score thresholds and colors
SCORE_THRESHOLDS = {
    'PASS': {'min': 80, 'color': '#22c55e', 'text': 'PASS'},
    'REVIEW': {'min': 60, 'color': '#f59e0b', 'text': 'REVIEW'},
    'FAIL': {'min': 0, 'color': '#ef4444', 'text': 'FAIL'}
}

# Finding categories with colors
FINDING_CATEGORIES = {
    "cookie_consent": ("Cookie Consent", "#f59e0b"),
    "privacy_policy": ("Privacy Policy", "#3b82f6"),
    "contact_info": ("Contact Information", "#10b981"),
    "trackers": ("Trackers Detected", "#ef4444"),
    "other": ("Other Issues", "#8b5cf6"),
}


def _get_score_status(score: int) -> tuple:
    """
    Get status and color based on score.
    
    Args:
        score: Compliance score (0-100)
        
    Returns:
        Tuple of (color, status_text)
    """
    if score >= SCORE_THRESHOLDS['PASS']['min']:
        return SCORE_THRESHOLDS['PASS']['color'], SCORE_THRESHOLDS['PASS']['text']
    elif score >= SCORE_THRESHOLDS['REVIEW']['min']:
        return SCORE_THRESHOLDS['REVIEW']['color'], SCORE_THRESHOLDS['REVIEW']['text']
    else:
        return SCORE_THRESHOLDS['FAIL']['color'], SCORE_THRESHOLDS['FAIL']['text']


def render_quick_results(results: Dict[str, Any]):
    """
    Render quick results with improved layout.
    
    Args:
        results: Scan results dictionary containing:
                 - score: int (0-100)
                 - grade: str (A-F)
                 - status: str (Compliant/Needs Work/At Risk)
                 - findings: dict of findings by category
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Large score display
        score = results.get("score", 0)
        grade = results.get("grade", "F")
        
        # Get color and status based on score
        color, status_text = _get_score_status(score)
        
        st.markdown(f"""
        <div class="score-display-container">
            <div class="score-display-value" style="color: {color};">{score}</div>
            <div class="score-display-max">/ 100</div>
            <div class="score-display-grade" style="color: {color};">Grade: {grade}</div>
            <div class="score-display-status">{status_text} - {results.get('status', 'Unknown')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Score breakdown chart
        st.markdown("**Score Breakdown**")
        
        breakdown = results.get("score_breakdown", {})
        if breakdown:
            breakdown_data = []
            for category, points in breakdown.items():
                breakdown_data.append({
                    "Category": category,
                    "Points": points
                })
            
            df = pd.DataFrame(breakdown_data)
            chart = alt.Chart(df).mark_bar(
                cornerRadiusTopLeft=4, cornerRadiusTopRight=4
            ).encode(
                x=alt.X('Category:N', sort=None, axis=alt.Axis(
                    labelColor='#b4bcd4', labelAngle=0, title=None
                )),
                y=alt.Y('Points:Q', scale=alt.Scale(domain=[0, 30]), axis=alt.Axis(
                    labelColor='#b4bcd4', title=None, gridColor='#2a3250'
                )),
                color=alt.Color('Category:N', scale=alt.Scale(
                    domain=['Cookie Consent', 'Privacy Policy', 'Contact Info', 'Trackers (0=best)'],
                    range=['#f59e0b', '#3b82f6', '#10b981', '#ef4444']
                ), legend=None),
                tooltip=['Category', 'Points']
            ).properties(height=200).configure_view(
                stroke='transparent', fill='transparent'
            ).configure_axis(domainColor='#2a3250')
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No breakdown data available")
    
    with col3:
        # Key stats
        st.markdown("**Summary**")
        
        stats_html = f"""
        <div class="stats-summary-box">
            <div class="stats-summary-item">
                <span class="stats-summary-label">URL:</span>
                <span class="stats-summary-value">{results.get("url", "N/A")}</span>
            </div>
            <div class="stats-summary-item">
                <span class="stats-summary-label">Scanned:</span>
                <span class="stats-summary-value">{results.get("scan_date", "N/A")}</span>
            </div>
            <div class="stats-summary-item">
                <span class="stats-summary-label">Status:</span>
                <span class="stats-summary-value status" style="color: {color};">{results.get("status", "Unknown")}</span>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)


def render_findings(findings: Dict[str, List[str]]):
    """
    Render findings in expandable sections.
    
    Args:
        findings: Dictionary of findings by category
                  - cookie_consent: list of issues
                  - privacy_policy: list of issues
                  - contact_info: list of issues
                  - trackers: list of detected trackers
    """
    st.markdown("### Detailed Findings")
    
    for key, (title, color) in FINDING_CATEGORIES.items():
        items = findings.get(key, [])
        if items:
            with st.expander(f"{title} ({len(items)} items)", expanded=False):
                for i, item in enumerate(items, 1):
                    st.markdown(f"**{i}.** {item}")
        else:
            st.success(f"{title} - No issues found")


def render_detailed_findings_table(findings: List[Dict[str, Any]]):
    """
    Render findings as a detailed table.
    
    Args:
        findings: List of finding dictionaries with:
                  - category: str
                  - issue: str
                  - severity: str (high/medium/low)
                  - recommendation: str
    """
    if not findings:
        st.info("No findings recorded for this scan")
        return
    
    df = pd.DataFrame(findings)
    
    # Color severity column
    def severity_color(severity: str) -> str:
        severity = severity.lower()
        if severity == "high":
            return "🔴 High"
        elif severity == "medium":
            return "🟡 Medium"
        else:
            return "🟢 Low"
    
    df["Severity"] = df.get("severity", "medium").apply(severity_color)
    
    st.dataframe(
        df[["Category", "Issue", "Severity", "Recommendation"]],
        width='stretch',
        hide_index=True
    )


def render_recommendations(recommendations: List[str]):
    """
    Render improvement recommendations.
    
    Args:
        recommendations: List of recommendation strings
    """
    if not recommendations:
        st.success("No recommendations - site is fully compliant! ✓")
        return
    
    st.markdown("### 💡 Recommendations for Improvement")
    
    for i, rec in enumerate(recommendations, 1):
        with st.container():
            col1, col2 = st.columns([0.5, 9.5])
            with col1:
                st.markdown(f"**{i}.**")
            with col2:
                st.markdown(rec)


def render_ai_analysis(analysis_text: str):
    """Render AI-powered privacy policy analysis output with proper markdown formatting."""
    if not analysis_text:
        st.info("No AI analysis available.")
        return
    
    # Use expandable container for better UI
    with st.expander("🤖 AI Compliance Analysis", expanded=True):
        # Render markdown properly to parse headers, bold, lists, etc.
        st.markdown(analysis_text)
