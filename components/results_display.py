"""Results display components."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
import html
from constants import is_detected

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

    # Find the dynamic tracker key (controller generates "Trackers (X found)")
    tracker_key = next((k for k in breakdown if k.startswith("Trackers")), None)
    tracker_count = len(results.get("trackers", []))

    # (display_name, breakdown_key, icon, color, css_cls, max_pts, finding_field)
    CATEGORIES = [
        ("Cookie Consent", "Cookie Consent", "🍪", "#f59e0b", "orange", 30, "cookie_consent"),
        ("Privacy Policy", "Privacy Policy", "📄", "#3b82f6", "blue",   30, "privacy_policy"),
        ("Contact Info",   "Contact Info",   "📬", "#10b981", "green",  20, "contact_info"),
        ("Trackers",       tracker_key,      "🔍", "#ef4444", "red",    20, None),
    ]

    cols = st.columns(4)
    for col, (display_name, lookup_key, icon, cat_color, css_cls, max_pts, finding_field) in zip(cols, CATEGORIES):
        pts = breakdown.get(lookup_key, 0) if lookup_key else 0
        pct = min(int(pts / max_pts * 100), 100) if max_pts else 0
        has_issues = pts < max_pts
        status_cls = "issues" if has_issues else "pass"
        status_label = "Issues found" if has_issues else "All clear"

        # Build one-line reason snippet
        if finding_field:
            raw_finding = str(results.get(finding_field, ""))
            # Trim verbose "Found ..." / "Not Found ..." to a short snippet
            if is_detected(raw_finding):
                reason = raw_finding[:70] + ("…" if len(raw_finding) > 70 else "")
            else:
                # Strip leading "Not Found" prefix if present for clarity
                trimmed = raw_finding.replace("Not Found", "").strip(" -–—")
                reason = (trimmed[:70] + "…") if len(trimmed) > 70 else (trimmed or "Not detected")
        else:
            # Trackers card — show count + first few domains
            trackers_list = results.get("trackers", [])
            if trackers_list:
                names = ", ".join(trackers_list[:2])
                extra = f" +{len(trackers_list)-2} more" if len(trackers_list) > 2 else ""
                reason = f"{tracker_count} tracker(s): {names}{extra}"
            else:
                reason = "No trackers detected"

        safe_cat_color = html.escape(cat_color)
        safe_display = html.escape(display_name)
        safe_reason = html.escape(reason)

        col.markdown(f"""
<div class="metric-card {css_cls}">
  <div class="metric-label">{icon}&nbsp; {safe_display}</div>
  <div class="metric-value" style="color:{safe_cat_color};">{pts}<span style="font-size:1rem;color:#8b949e;font-weight:400;"> / {max_pts}</span></div>
  <div class="progress-bar-track">
    <div class="progress-bar-fill" style="width:{pct}%;background:{safe_cat_color};"></div>
  </div>
  <div class="category-status {status_cls}">{status_label}</div>
  <div class="category-reason">{safe_reason}</div>
</div>
""", unsafe_allow_html=True)


def render_findings(findings):
    """
    Render findings in expandable sections.

    Accepts either:
      - List[Dict] with keys: category, issue, severity, passed  (new format)
      - Dict[str, List[str]] keyed by category slug             (legacy format)
    """
    st.markdown("### Detailed Findings")

    SEVERITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    if isinstance(findings, list):
        # New structured format from controller — render as styled cards
        if not findings:
            st.info("No findings recorded for this scan.")
            return

        severity_css = {"high": "high", "medium": "medium", "low": "pass"}
        severity_badge_css = {"high": "badge-high", "medium": "badge-medium", "low": "badge-pass"}
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        severity_label = {"high": "High", "medium": "Medium", "low": "Low"}

        cards_html = ""
        for item in findings:
            category = html.escape(item.get("category", "Unknown"))
            issue = html.escape(item.get("issue", ""))
            severity = item.get("severity", "low")
            passed = item.get("passed", True)

            card_cls = "pass" if passed else severity_css.get(severity, "medium")
            badge_cls = "badge-pass" if passed else severity_badge_css.get(severity, "badge-medium")
            icon = "✅" if passed else severity_icon.get(severity, "🟡")
            badge_txt = "Pass" if passed else severity_label.get(severity, "Medium")

            cards_html += f"""
<div class="finding-card {card_cls}">
  <div class="finding-card-icon">{icon}</div>
  <div class="finding-card-body">
    <div class="finding-card-title">{category}</div>
    <div class="finding-card-text">{issue}</div>
  </div>
  <span class="finding-card-badge {badge_cls}">{badge_txt}</span>
</div>"""

        st.markdown(cards_html, unsafe_allow_html=True)
    elif isinstance(findings, dict):
        # Legacy dict format
        for key, (title, color) in FINDING_CATEGORIES.items():
            items = findings.get(key, [])
            if items:
                with st.expander(f"{title} ({len(items)} items)", expanded=False):
                    for i, item in enumerate(items, 1):
                        st.markdown(f"**{i}.** {item}")
            else:
                st.success(f"{title} - No issues found")
    else:
        st.info("No findings recorded for this scan.")


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
    Render improvement recommendations as styled numbered list.

    Args:
        recommendations: List of recommendation strings
    """
    if not recommendations:
        st.success("No recommendations — site is fully compliant!")
        return

    st.markdown("### Recommendations for Improvement")

    items_html = '<div style="background:rgba(15,20,40,0.5);border:1px solid #1e2647;border-radius:12px;padding:0.5rem 1.25rem;">'
    for i, rec in enumerate(recommendations, 1):
        safe_rec = html.escape(str(rec))
        items_html += f"""
<div class="rec-item">
  <div class="rec-num">{i}</div>
  <div class="rec-text">{safe_rec}</div>
</div>"""
    items_html += "</div>"
    st.markdown(items_html, unsafe_allow_html=True)


def render_ai_analysis(analysis_text: str):
    """Render AI-powered privacy policy analysis output with proper markdown formatting."""
    if not analysis_text:
        st.info("No AI analysis available.")
        return
    
    # Use expandable container for better UI
    with st.expander("🤖 AI Compliance Analysis", expanded=True):
        st.markdown(analysis_text)
