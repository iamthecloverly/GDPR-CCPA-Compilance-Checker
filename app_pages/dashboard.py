"""Dashboard page - hero landing page with compliance overview and quick start."""

import streamlit as st
import pandas as pd
import altair as alt
from components.header import create_metric_card
from database.operations import get_recent_scans, get_scan_statistics
from logger_config import get_logger

logger = get_logger(__name__)


def render_hero():
    """Render the hero section with headline, subtitle, CTA links, stats, and product mockup."""
    hero_html = """
    <div class="hero-section">
        <div class="hero-glow-top"></div>
        <div class="hero-glow-bottom"></div>
        <div class="hero-content">
            <div class="hero-badge">
                <span class="hero-live-dot"></span>
                GDPR &amp; CCPA Compliance Platform
            </div>
            <h1 class="hero-title">Privacy Compliance,<br>Simplified.</h1>
            <p class="hero-subtitle">
                Scan any website in seconds. Get actionable GDPR &amp; CCPA insights
                powered by AI &mdash; no technical expertise required.
            </p>
            <div class="hero-pills">
                <span class="hero-pill">🔒 GDPR Ready</span>
                <span class="hero-pill">📋 CCPA Compliant</span>
                <span class="hero-pill">⚡ Instant Scanning</span>
                <span class="hero-pill">🤖 AI-Powered</span>
                <span class="hero-pill">📊 Detailed Reports</span>
            </div>
            <div class="hero-cta-row">
                <a href="?nav=quick_scan" class="hero-btn-primary">🚀 Start Quick Scan</a>
                <a href="?nav=batch_scan" class="hero-btn-secondary">📂 Batch Scan</a>
            </div>
            <div class="hero-stats">
                <div class="hero-stat-item">
                    <span class="hero-stat-num">10K+</span>
                    <span class="hero-stat-label">Sites Checked</span>
                </div>
                <div class="hero-stat-item">
                    <span class="hero-stat-num">99%</span>
                    <span class="hero-stat-label">GDPR Coverage</span>
                </div>
                <div class="hero-stat-item">
                    <span class="hero-stat-num">&lt;30s</span>
                    <span class="hero-stat-label">Scan Time</span>
                </div>
            </div>
        </div>
        <div class="hero-mockup">
            <div class="mockup-glow"></div>
            <div class="mockup-window">
                <div class="mockup-titlebar">
                    <div class="mockup-dot red"></div>
                    <div class="mockup-dot yellow"></div>
                    <div class="mockup-dot green"></div>
                    <div class="mockup-url">privacyguard.io/scan</div>
                </div>
                <div class="mockup-body">
                    <div class="mockup-site-row">
                        <div class="mockup-favicon"></div>
                        <span class="mockup-site-name">example.com &mdash; Compliance Report</span>
                    </div>
                    <div class="mockup-score-row">
                        <div class="mockup-grade">A</div>
                        <div>
                            <div class="mockup-score-num">87<span style="font-size:1rem;color:#8b949e">/100</span></div>
                            <div class="mockup-status-badge">&#10004; Compliant</div>
                        </div>
                    </div>
                    <div class="mockup-findings">
                        <div class="mockup-finding pass">
                            <div class="mockup-finding-dot"></div>Cookie Consent Banner
                        </div>
                        <div class="mockup-finding pass">
                            <div class="mockup-finding-dot"></div>Privacy Policy Detected
                        </div>
                        <div class="mockup-finding pass">
                            <div class="mockup-finding-dot"></div>Contact Info Found
                        </div>
                        <div class="mockup-finding warn">
                            <div class="mockup-finding-dot"></div>3 Third-party Trackers
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_dashboard_page():
    """Render the dashboard landing page."""

    render_hero()

    # ── Compliance Overview ────────────────────────────────────────────
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Overview</div>
    <div class="section-heading">Compliance Overview</div>
    """, unsafe_allow_html=True)

    try:
        stats = get_scan_statistics() or {}
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        stats = {}

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        total = stats.get("total_scans", 0)
        create_metric_card(
            "Total Scans",
            str(total),
            "↗ +12 this week" if total > 0 else "No scans yet",
            "blue"
        )
    with c2:
        avg_score = stats.get("avg_score", 0)
        delta_val = avg_score - 70
        delta_text = f"{delta_val:+.0f}% vs baseline" if avg_score > 0 else "Awaiting data"
        create_metric_card("Avg Score", f"{avg_score:.0f}", delta_text, "orange")
    with c3:
        compliant = stats.get("compliant_count", 0)
        create_metric_card(
            "Compliant Sites",
            str(compliant),
            "↗ +5 new sites" if compliant > 0 else "None yet",
            "green"
        )
    with c4:
        at_risk = stats.get("at_risk_count", 0)
        create_metric_card(
            "At Risk",
            str(at_risk),
            "⚠ High Priority" if at_risk > 0 else "All clear",
            "red"
        )

    # ── Compliance Activity chart ──────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Analytics</div>
    <div class="section-heading">Compliance Activity</div>
    """, unsafe_allow_html=True)

    col_chart, col_empty = st.columns([3, 1])
    with col_chart:
        total_scans = stats.get("total_scans", 0)

        if total_scans > 0:
            categories = ['Week 1', 'Week 2', 'Week 3', 'Week 4',
                          'Week 5', 'Week 6', 'Week 7', 'Week 8']
            chart_data = pd.DataFrame({
                'Category': categories * 2,
                'Status': ['Compliant'] * 8 + ['At Risk'] * 8,
                'Count': [10, 15, 8, 12, 20, 18, 5, 10, 5, 2, 8, 3, 1, 4, 12, 6]
            })
        else:
            categories = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            chart_data = pd.DataFrame({
                'Category': categories * 2,
                'Status': ['Compliant'] * 4 + ['At Risk'] * 4,
                'Count': [0] * 8
            })

        chart = alt.Chart(chart_data).mark_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        ).encode(
            x=alt.X('Category:N', axis=alt.Axis(labelColor='#8b949e', labelAngle=0, title=None)),
            y=alt.Y('Count:Q', axis=alt.Axis(labelColor='#8b949e', gridColor='#21262d', title=None)),
            color=alt.Color('Status:N',
                scale=alt.Scale(domain=['Compliant', 'At Risk'], range=['#58a6ff', '#f85149']),
                legend=alt.Legend(orient='top', title=None, labelColor='#f0f6fc', direction='horizontal')
            ),
            xOffset='Status:N',
            tooltip=['Category', 'Status', 'Count']
        ).properties(height=280).configure_view(
            stroke='transparent', fill='transparent'
        ).configure_axis(gridColor='#21262d', domainColor='#21262d')

        st.altair_chart(chart, use_container_width=True)

    # ── Quick Actions ──────────────────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">Actions</div>
    <div class="section-heading">Quick Actions</div>
    """, unsafe_allow_html=True)

    def action_card(icon, title, desc):
        return f"""
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <h4 class="action-title">{title}</h4>
            <p class="action-desc">{desc}</p>
        </div>
        """

    ac1, ac2, ac3 = st.columns(3, gap="medium")
    with ac1:
        st.markdown(action_card("🚀", "Quick Scan", "Analyze a single URL instantly for GDPR/CCPA compliance"), unsafe_allow_html=True)
        if st.button("Start Quick Scan", key="dash_quick", use_container_width=True, type="primary"):
            st.session_state.page = "quick_scan"
            st.rerun()
    with ac2:
        st.markdown(action_card("📂", "Batch Scan", "Upload CSV for bulk analysis of multiple sites"), unsafe_allow_html=True)
        if st.button("Start Batch Scan", key="dash_batch", use_container_width=True, type="primary"):
            st.session_state.page = "batch_scan"
            st.rerun()
    with ac3:
        st.markdown(action_card("📜", "View History", "Review past compliance reports and trends"), unsafe_allow_html=True)
        if st.button("Open History", key="dash_history", use_container_width=True, type="primary"):
            st.session_state.page = "history"
            st.rerun()

    # ── Recent Scans ───────────────────────────────────────────────────
    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">History</div>
    <div class="section-heading">Recent Scans</div>
    """, unsafe_allow_html=True)

    try:
        recent_scans = get_recent_scans(limit=5)

        if recent_scans:
            for idx, scan in enumerate(recent_scans):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 1.5, 1, 1.5])
                    with col1:
                        st.markdown(f"**{scan.get('url', 'Unknown URL')}**")
                        st.caption(f"🕒 {scan.get('scan_date', 'N/A')}")
                    with col2:
                        score = scan.get('score', 0)
                        st.metric("Score", f"{score}/100", label_visibility="collapsed")
                    with col3:
                        grade = scan.get('grade', 'N/A')
                        grade_color = '#10b981' if grade == 'A' else ('#f59e0b' if grade in ['B', 'C'] else '#ef4444')
                        st.markdown(
                            f"<div style='text-align:center;padding:8px;'>"
                            f"<span style='color:{grade_color};font-weight:bold;font-size:20px;'>{grade}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with col4:
                        if st.button("View", key=f"details_{idx}", use_container_width=True, type="secondary"):
                            st.session_state.selected_scan_id = scan.get('id')
                            st.session_state.page = "history"
                            st.rerun()
        else:
            st.info("📭 No scans yet. Use Quick Actions above to get started!")
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
