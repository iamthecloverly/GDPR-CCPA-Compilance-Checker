"""Results display components."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
import html

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
    Render quick results: score hero card (row 1) + 4 category metric cards (row 2).

    Args:
        results: Scan results dictionary containing:
                 - score: int (0-100)
                 - grade: str (A-F)
                 - status: str (Compliant/Needs Work/At Risk)
                 - score_breakdown: dict of category → points
    """
    score = results.get("score", 0)
    grade = results.get("grade", "F")
    color, status_text = _get_score_status(score)

    # ── Row 1: Score hero card ────────────────────────────────────────────
    safe_score = html.escape(str(score))
    safe_grade = html.escape(str(grade))
    safe_color = html.escape(str(color))
    safe_status_text = html.escape(str(status_text))
    safe_results_status = html.escape(str(results.get("status", "Unknown")))
    safe_url = html.escape(str(results.get("url", "N/A")))
    safe_date = html.escape(str(results.get("scan_date", "N/A")))

    st.markdown(f"""
<div class="score-hero-card">
  <div class="score-hero-left">
    <div class="score-hero-number" style="color:{safe_color};">{safe_score}</div>
    <div class="score-hero-max">/ 100</div>
  </div>
  <div class="score-hero-center">
    <div class="score-hero-grade" style="color:{safe_color};">Grade&nbsp;{safe_grade}</div>
    <div class="score-hero-badge">{safe_status_text} &middot; {safe_results_status}</div>
  </div>
  <div class="score-hero-right">
    <div class="score-hero-meta">
      <span>URL</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{safe_url}<br>
      <span>Scanned</span>&nbsp;&nbsp;&nbsp;{safe_date}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Row 2: Category metric cards with progress bars ───────────────────
    breakdown = results.get("score_breakdown", {})

    CATEGORIES = [
        ("Cookie Consent", "🍪", "#f59e0b", "orange"),
        ("Privacy Policy", "📄", "#3b82f6", "blue"),
        ("Contact Info",   "📬", "#10b981", "green"),
        ("Trackers (0=best)", "🔍", "#ef4444", "red"),
    ]

    cols = st.columns(4)
    for col, (name, icon, cat_color, css_cls) in zip(cols, CATEGORIES):
        pts = breakdown.get(name, 0)
        max_pts = 30
        pct = min(int(pts / max_pts * 100), 100)
        # For trackers lower is better: full bar = 0 trackers (score pts = 30)
        has_issues = pts < max_pts
        status_cls = "issues" if has_issues else "pass"
        status_label = "Issues found" if has_issues else "All clear"
        safe_cat_color = html.escape(cat_color)
        safe_name = html.escape(name)
        safe_icon = icon  # emoji — safe
        col.markdown(f"""
<div class="metric-card {css_cls}">
  <div class="metric-label">{safe_icon}&nbsp; {safe_name}</div>
  <div class="metric-value" style="color:{safe_cat_color};">{pts}<span style="font-size:1rem;color:#8b949e;font-weight:400;"> / {max_pts}</span></div>
  <div class="progress-bar-track">
    <div class="progress-bar-fill" style="width:{pct}%;background:{safe_cat_color};"></div>
  </div>
  <div class="category-status {status_cls}">{status_label}</div>
</div>
""", unsafe_allow_html=True)


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
