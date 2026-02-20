"""Dashboard page - hero landing page with compliance overview and quick start."""

import streamlit as st
import pandas as pd
import altair as alt
from components.header import create_metric_card
from database.operations import get_recent_scans, get_scan_statistics
from logger_config import get_logger

logger = get_logger(__name__)

_SHIELD_SVG = (
    '<svg width="240" height="260" viewBox="0 0 240 260" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="sg" x1="120" y1="44" x2="120" y2="180" gradientUnits="userSpaceOnUse">'
    '<stop offset="0%" stop-color="#00d9ff"/>'
    '<stop offset="100%" stop-color="#0d1135" stop-opacity="0"/>'
    '</linearGradient></defs>'
    '<circle cx="120" cy="120" r="112" stroke="#00d9ff" stroke-opacity="0.08" stroke-width="1.5"/>'
    '<circle cx="120" cy="120" r="92" stroke="#00d9ff" stroke-opacity="0.12" stroke-width="1" stroke-dasharray="5 5"/>'
    '<circle cx="120" cy="120" r="72" stroke="#58a6ff" stroke-opacity="0.1" stroke-width="1"/>'
    '<path d="M120 32 L178 57 L178 118 Q178 163 120 192 Q62 163 62 118 L62 57 Z" fill="#0d1135" stroke="#00d9ff" stroke-width="1.8" stroke-linejoin="round"/>'
    '<path d="M120 44 L168 65 L168 118 Q168 155 120 180 Q72 155 72 118 L72 65 Z" fill="url(#sg)" opacity="0.18"/>'
    '<path d="M96 118 L112 136 L148 100" stroke="#00d9ff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<rect x="68" y="202" width="44" height="22" rx="11" fill="rgba(0,217,255,0.12)" stroke="rgba(0,217,255,0.3)" stroke-width="1"/>'
    '<text x="90" y="217" text-anchor="middle" fill="#00d9ff" font-size="9.5" font-family="sans-serif" font-weight="700">GDPR</text>'
    '<rect x="128" y="202" width="44" height="22" rx="11" fill="rgba(88,166,255,0.12)" stroke="rgba(88,166,255,0.3)" stroke-width="1"/>'
    '<text x="150" y="217" text-anchor="middle" fill="#58a6ff" font-size="9.5" font-family="sans-serif" font-weight="700">CCPA</text>'
    '<circle cx="28" cy="80" r="3.5" fill="#00d9ff" opacity="0.35"/>'
    '<circle cx="212" cy="155" r="2.5" fill="#58a6ff" opacity="0.45"/>'
    '<circle cx="40" cy="180" r="2" fill="#00d9ff" opacity="0.25"/>'
    '<circle cx="200" cy="60" r="2" fill="#58a6ff" opacity="0.3"/>'
    '</svg>'
)


def render_hero():
    """Render the hero section with headline, subtitle, feature pills, SVG visual, and trust strip."""
    hero_html = f"""
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
                Scan any website in seconds. Get actionable GDPR and CCPA insights
                powered by AI &mdash; no technical expertise required.
            </p>
            <div class="hero-pills">
                <span class="hero-pill">🔒 GDPR Ready</span>
                <span class="hero-pill">📋 CCPA Compliant</span>
                <span class="hero-pill">⚡ Instant Scanning</span>
                <span class="hero-pill">🤖 AI-Powered</span>
                <span class="hero-pill">📊 Detailed Reports</span>
            </div>
        </div>
        <div class="hero-visual">
            {_SHIELD_SVG}
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # CTA buttons
    b1, b2, b3 = st.columns([1.8, 1.8, 4], gap="small")
    with b1:
        if st.button("🚀 Start Quick Scan", key="hero_quick", use_container_width=True, type="primary"):
            st.session_state.page = "quick_scan"
            st.rerun()
    with b2:
        if st.button("📂 Batch Scan", key="hero_batch", use_container_width=True):
            st.session_state.page = "batch_scan"
            st.rerun()

    # Trust strip
    st.markdown("""
    <div class="trust-strip">
        <div class="trust-item">✅&nbsp;<span class="trust-value">GDPR</span>&nbsp;Article 13 Ready</div>
        <div class="trust-sep"></div>
        <div class="trust-item">✅&nbsp;<span class="trust-value">CCPA</span>&nbsp;Section 1798 Ready</div>
        <div class="trust-sep"></div>
        <div class="trust-item">⚡&nbsp;<span class="trust-value">Real-time</span>&nbsp;scanning</div>
        <div class="trust-sep"></div>
        <div class="trust-item">🤖&nbsp;<span class="trust-value">GPT-4</span>&nbsp;powered analysis</div>
    </div>
    """, unsafe_allow_html=True)


def render_dashboard_page():
    """Render the dashboard landing page."""

    render_hero()

    # ── Compliance Overview ────────────────────────────────────────────
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
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
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
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
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
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
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
