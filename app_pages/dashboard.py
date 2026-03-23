"""Dashboard page - hero landing page with compliance overview and quick start."""

import streamlit as st
import pandas as pd
import altair as alt
import html
from components.header import create_metric_card
from database.operations import get_recent_scans, get_scan_statistics, get_all_scans
from logger_config import get_logger

logger = get_logger(__name__)


def render_hero(stats: dict):
    """Render the hero section with real stats, honest copy, and feature pills."""
    from config import Config

    total_scans = stats.get("total_scans", 0)

    # Build pills inline (no blank lines from empty interpolation)
    pill_labels = ["Cookie Consent", "Privacy Policy", "Tracker Detection", "Compliance Score", "PDF &amp; CSV Export"]
    if Config.OPENAI_API_KEY:
        pill_labels.append("AI Analysis")
    pills_html = "".join(f'<span class="hero-pill">{p}</span>' for p in pill_labels)

    # Stats only shown when data exists
    if total_scans > 0:
        avg = stats.get("avg_score", 0)
        compliant = stats.get("compliant_count", 0)
        stats_html = (
            f'<div class="hero-stats">'
            f'<div class="hero-stat-item"><span class="hero-stat-num">{total_scans}</span><span class="hero-stat-label">Scans Run</span></div>'
            f'<div class="hero-stat-item"><span class="hero-stat-num">{avg:.0f}/100</span><span class="hero-stat-label">Avg Score</span></div>'
            f'<div class="hero-stat-item"><span class="hero-stat-num">{compliant}</span><span class="hero-stat-label">Sites Compliant</span></div>'
            f'</div>'
        )
    else:
        stats_html = ""

    st.markdown(f"""<div class="hero-section">
<div class="hero-glow-top"></div>
<div class="hero-glow-bottom"></div>
<div class="hero-content">
<div class="hero-badge"><span class="hero-live-dot"></span>GDPR &amp; CCPA Compliance Scanner</div>
<h1 class="hero-title">Privacy Compliance,<br>Simplified.</h1>
<p class="hero-subtitle">Scan any website for GDPR and CCPA compliance signals in seconds. Detects cookie consent, privacy policies, third-party trackers, and contact information &mdash; with a clear score and actionable report.</p>
<div class="hero-pills">{pills_html}</div>
<div class="hero-cta-row"><a href="?nav=quick_scan" class="hero-btn-primary" target="_self">Start Quick Scan</a><a href="?nav=batch_scan" class="hero-btn-secondary" target="_self">Batch Scan</a></div>
{stats_html}</div>
<div class="hero-mockup">
<div class="mockup-glow"></div>
<div class="mockup-window">
<div class="mockup-titlebar"><div class="mockup-dot red"></div><div class="mockup-dot yellow"></div><div class="mockup-dot green"></div><div class="mockup-url">compliance-checker / scan</div></div>
<div class="mockup-body">
<div class="mockup-site-row"><div class="mockup-favicon"></div><span class="mockup-site-name">example.com &mdash; Compliance Report</span></div>
<div class="mockup-score-row"><div class="mockup-grade">A</div><div><div class="mockup-score-num">87<span style="font-size:1rem;color:#a1a1aa">/100</span></div><div class="mockup-status-badge">&#10004; Compliant</div></div></div>
<div class="mockup-findings">
<div class="mockup-finding pass"><div class="mockup-finding-dot"></div>Cookie Consent Banner</div>
<div class="mockup-finding pass"><div class="mockup-finding-dot"></div>Privacy Policy Detected</div>
<div class="mockup-finding pass"><div class="mockup-finding-dot"></div>Contact Info Found</div>
<div class="mockup-finding warn"><div class="mockup-finding-dot"></div>3 Third-party Trackers</div>
</div></div></div></div></div>""", unsafe_allow_html=True)


def render_dashboard_page():
    """Render the dashboard landing page."""
    try:
        stats = get_scan_statistics() or {}
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        stats = {}

    render_hero(stats)

    # ── Compliance Overview ────────────────────────────────────────────
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Overview</div>
    <h2 class="section-heading">Compliance Overview</h2>
""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        total = stats.get("total_scans", 0)
        create_metric_card(
            "Total Scans",
            str(total),
            "Sites scanned" if total > 0 else "No scans yet",
            "blue"
        )
    with c2:
        avg_score = stats.get("avg_score", 0)
        delta_text = f"Average compliance score" if avg_score > 0 else "Awaiting data"
        create_metric_card("Avg Score", f"{avg_score:.0f}", delta_text, "orange")
    with c3:
        compliant = stats.get("compliant_count", 0)
        create_metric_card(
            "Compliant Sites",
            str(compliant),
            "Score ≥ 80" if compliant > 0 else "None yet",
            "green"
        )
    with c4:
        at_risk = stats.get("at_risk_count", 0)
        create_metric_card(
            "At Risk",
            str(at_risk),
            "Score < 60" if at_risk > 0 else "All clear",
            "red"
        )

    # ── Compliance Activity chart ──────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Analytics</div>
    <h2 class="section-heading">Compliance Activity</h2>
""", unsafe_allow_html=True)

    col_chart, col_dist = st.columns([3, 2])
    with col_chart:
        try:
            scans = get_all_scans()
        except Exception:
            scans = []

        if scans:
            scan_df = pd.DataFrame(scans)
            scan_df["scan_date"] = pd.to_datetime(scan_df["scan_date"])
            scan_df = scan_df.sort_values("scan_date").tail(50)

            line_chart = (
                alt.Chart(scan_df)
                .mark_line(color="#f59e0b", strokeWidth=2, interpolate="monotone")
                .encode(
                    x=alt.X("scan_date:T", title=None, axis=alt.Axis(labelColor="#a1a1aa", format="%b %d")),
                    y=alt.Y("score:Q", title="Score", scale=alt.Scale(domain=[0, 100]),
                            axis=alt.Axis(labelColor="#a1a1aa", gridColor="#27272a")),
                    tooltip=[
                        alt.Tooltip("scan_date:T", title="Date", format="%b %d %Y"),
                        alt.Tooltip("url:N", title="URL"),
                        alt.Tooltip("score:Q", title="Score"),
                        alt.Tooltip("grade:N", title="Grade"),
                    ],
                )
            )
            points = (
                alt.Chart(scan_df)
                .mark_circle(size=55, color="#f59e0b", opacity=0.75)
                .encode(
                    x=alt.X("scan_date:T"),
                    y=alt.Y("score:Q"),
                    color=alt.Color(
                        "score:Q",
                        scale=alt.Scale(
                            domain=[0, 60, 80, 100],
                            range=["#f85149", "#f85149", "#d29922", "#3fb950"],
                        ),
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("url:N", title="URL"),
                        alt.Tooltip("score:Q", title="Score"),
                        alt.Tooltip("grade:N", title="Grade"),
                    ],
                )
            )
            st.altair_chart(
                (line_chart + points)
                .properties(height=260)
                .configure_view(stroke="transparent", fill="transparent")
                .configure_axis(gridColor="#27272a", domainColor="#27272a"),
                use_container_width=True,
            )
        else:
            st.markdown("""
            <div class="empty-state" style="height:200px;">
                <div class="empty-state-icon">📈</div>
                <p class="empty-state-title">No scan data yet</p>
                <p class="empty-state-body">Run your first scan to see the score trend chart.</p>
            </div>
            """, unsafe_allow_html=True)

    with col_dist:
        st.caption("GRADE DISTRIBUTION")
        if scans:
            dist_df = pd.DataFrame(scans)
            grade_counts = dist_df["grade"].value_counts().reset_index()
            grade_counts.columns = ["Grade", "Count"]
            grade_order = ["A", "B", "C", "D", "F"]
            color_map = {"A": "#3fb950", "B": "#58a6ff", "C": "#d29922", "D": "#f0883e", "F": "#f85149"}

            donut = (
                alt.Chart(grade_counts)
                .mark_arc(innerRadius=55, outerRadius=95, cornerRadius=4)
                .encode(
                    theta=alt.Theta("Count:Q"),
                    color=alt.Color(
                        "Grade:N",
                        scale=alt.Scale(domain=grade_order, range=[color_map[g] for g in grade_order]),
                        legend=alt.Legend(orient="bottom", title=None, labelColor="#a1a1aa",
                                          columns=5, direction="horizontal"),
                    ),
                    tooltip=["Grade:N", "Count:Q"],
                )
                .properties(height=220)
                .configure_view(stroke="transparent", fill="transparent")
            )
            st.altair_chart(donut, use_container_width=True)
        else:
            st.markdown("""
            <div class="empty-state" style="height:200px;">
                <div class="empty-state-icon">🏅</div>
                <p class="empty-state-title">No grade data</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick Actions ──────────────────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Actions</div>
    <h2 class="section-heading">Quick Actions</h2>

    <div class="actions-grid">
      <a href="?nav=quick_scan" class="action-card-v2" target="_self">
        <div class="action-card-icon-wrap amber">⚡</div>
        <div class="action-card-body">
          <h4 class="action-card-title">Quick Scan</h4>
          <p class="action-card-desc">Analyze a single website for GDPR &amp; CCPA compliance signals in seconds. Get an instant score and actionable report.</p>
        </div>
        <span class="action-cta-btn primary">Start Quick Scan &rarr;</span>
      </a>
      <a href="?nav=batch_scan" class="action-card-v2" target="_self">
        <div class="action-card-icon-wrap blue">📂</div>
        <div class="action-card-body">
          <h4 class="action-card-title">Batch Scan</h4>
          <p class="action-card-desc">Upload a CSV to scan multiple websites at once. Perfect for auditing large portfolios of sites efficiently.</p>
        </div>
        <span class="action-cta-btn blue-btn">Start Batch Scan &rarr;</span>
      </a>
      <a href="?nav=history" class="action-card-v2" target="_self">
        <div class="action-card-icon-wrap green">📜</div>
        <div class="action-card-body">
          <h4 class="action-card-title">Scan History</h4>
          <p class="action-card-desc">Browse past compliance reports, compare sites side-by-side, and export data as CSV, JSON, or PDF.</p>
        </div>
        <span class="action-cta-btn green-btn">View History &rarr;</span>
      </a>
    </div>
    """, unsafe_allow_html=True)

    # ── Recent Scans ───────────────────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">History</div>
    <h2 class="section-heading">Recent Scans</h2>
""", unsafe_allow_html=True)

    try:
        recent_scans = get_recent_scans(limit=5)

        if recent_scans:
            rows_html = '<div class="recent-scans-list">'
            for scan in recent_scans:
                score = scan.get("score", 0)
                grade = scan.get("grade", "N/A")
                url = html.escape(str(scan.get("url", "Unknown URL")))
                date = html.escape(str(scan.get("scan_date", "N/A")))

                if grade == "A":
                    grade_color = "#3fb950"
                    grade_bg = "rgba(63,185,80,0.10)"
                    grade_border = "rgba(63,185,80,0.28)"
                elif grade in ("B", "C"):
                    grade_color = "#f59e0b"
                    grade_bg = "rgba(245,158,11,0.10)"
                    grade_border = "rgba(245,158,11,0.28)"
                else:
                    grade_color = "#f85149"
                    grade_bg = "rgba(248,81,73,0.10)"
                    grade_border = "rgba(248,81,73,0.28)"

                score_pct = min(int(score), 100)
                bar_color = grade_color

                rows_html += f"""
<div class="recent-scan-row">
  <div class="recent-scan-url">
    <div class="recent-scan-domain">{url}</div>
    <div class="recent-scan-date">&#128337; {date}</div>
  </div>
  <div class="recent-scan-score-wrap">
    <div class="recent-scan-score-num">{score}<span class="recent-scan-score-max">/100</span></div>
    <div class="recent-scan-bar-track">
      <div class="recent-scan-bar-fill" style="width:{score_pct}%;background:{bar_color};"></div>
    </div>
  </div>
  <div class="recent-scan-grade" style="color:{grade_color};background:{grade_bg};border:1px solid {grade_border};">{html.escape(str(grade))}</div>
  <a href="?nav=history" class="recent-scan-view-btn" target="_self">View &rarr;</a>
</div>"""
            rows_html += "</div>"
            st.markdown(rows_html, unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="empty-state" style="min-height:140px;">
  <div class="empty-state-icon">&#128205;</div>
  <p class="empty-state-title">No scans yet</p>
  <p class="empty-state-body">Use the Quick Actions above to run your first compliance scan.</p>
</div>""", unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"Error fetching recent scans: {e}")
        st.info("Recent scans will appear after your first scan")


def main():
    """Main function for dashboard page."""
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    render_dashboard_page()


if __name__ == "__main__":
    main()
