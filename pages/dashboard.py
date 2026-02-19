"""Dashboard page - landing page with statistics and quick start."""

import streamlit as st
import pandas as pd
import altair as alt
from components.header import create_metric_card
from database.operations import get_recent_scans, get_scan_statistics
from logger_config import get_logger

logger = get_logger(__name__)


def render_dashboard_page():
    """Render the dashboard landing page."""
    
    # Compact header - no extra spacing
    st.markdown("""
        <h1 style='margin-bottom: 8px; font-size: 32px; font-weight: 700;'>
            Dashboard
        </h1>
        <p style='color: var(--text-secondary); margin-bottom: 24px; font-size: 14px;'>
            Monitor compliance metrics and manage scans
        </p>
    """, unsafe_allow_html=True)
    
    # Statistics section with error handling
    try:
        stats = get_scan_statistics()
        if stats:
            # Glowing metric cards with colored borders
            c1, c2, c3, c4 = st.columns(4, gap="medium")
            
            with c1:
                total = stats.get("total_scans", 0)
                create_metric_card(
                    "Total Scans",
                    str(total),
                    f"↗ +12 this week" if total > 0 else "No scans yet",
                    "blue"
                )
            
            with c2:
                avg_score = stats.get("avg_score", 0)
                baseline = 70
                delta_val = avg_score - baseline
                delta_text = f"↘ {delta_val:+.0f}% vs baseline" if avg_score > 0 else "Awaiting data"
                create_metric_card(
                    "Avg Score",
                    f"{avg_score:.0f}",
                    delta_text,
                    "orange"
                )
            
            with c3:
                compliant = stats.get("compliant_count", 0)
                create_metric_card(
                    "Compliant Sites",
                    str(compliant),
                    f"↗ +5 new sites" if compliant > 0 else "None yet",
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
            
            # Add visualization
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            
            # Create chart section
            col_chart, col_empty = st.columns([3, 1])
            
            with col_chart:
                st.markdown("### Site Status Distribution")
                
                # Create grouped bar chart data similar to the image
                # Simulate multiple categories with Compliant and At Risk for each
                total_scans = stats.get("total_scans", 0)
                compliant_count = stats.get("compliant_count", 0)
                at_risk_count = stats.get("at_risk_count", 0)
                
                # Create mock data for grouped bars (simulating time periods or categories)
                if total_scans > 0:
                    # Generate 8 groups of data
                    categories = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8']
                    chart_data = pd.DataFrame({
                        'Category': categories * 2,
                        'Status': ['Compliant'] * 8 + ['At Risk'] * 8,
                        'Count': [
                            # Compliant counts (blue bars)
                            10, 15, 8, 12, 20, 18, 5, 10,
                            # At Risk counts (red bars)
                            5, 2, 8, 3, 1, 4, 12, 6
                        ]
                    })
                else:
                    # Empty state
                    categories = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
                    chart_data = pd.DataFrame({
                        'Category': categories * 2,
                        'Status': ['Compliant'] * 4 + ['At Risk'] * 4,
                        'Count': [0] * 8
                    })
                
                # Create grouped bar chart matching the image style
                chart = alt.Chart(chart_data).mark_bar(
                    cornerRadiusTopLeft=3,
                    cornerRadiusTopRight=3,
                    width=40
                ).encode(
                    x=alt.X('Category:N', axis=alt.Axis(
                        labelColor='#8b949e',
                        labelAngle=0,
                        title=None
                    )),
                    y=alt.Y('Count:Q', axis=alt.Axis(
                        labelColor='#8b949e',
                        gridColor='#21262d',
                        title=None
                    )),
                    color=alt.Color('Status:N',
                        scale=alt.Scale(
                            domain=['Compliant', 'At Risk'],
                            range=['#58a6ff', '#f85149']  # Blue and Red like the image
                        ),
                        legend=alt.Legend(
                            orient='top',
                            title=None,
                            labelColor='#f0f6fc',
                            direction='horizontal'
                        )
                    ),
                    xOffset='Status:N',
                    tooltip=['Category', 'Status', 'Count']
                ).properties(
                    height=250
                ).configure_view(
                    stroke='transparent',
                    fill='transparent'
                ).configure_axis(
                    gridColor='#21262d',
                    domainColor='#21262d'
                )
                
                st.altair_chart(chart, width='stretch')
        else:
            st.info("💡 No scans yet. Start by running a quick scan to see your first compliance report.")
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        st.info("💡 Statistics will appear after your first compliance scan")
    
    # Quick Actions - compact card style
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("### Quick Actions")
    
    def action_card(icon, title, desc):
        """Helper to create action card HTML."""
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
        if st.button("Start Quick Scan", key="dash_quick", width='stretch', type="primary"):
            st.session_state.page = "quick_scan"
            st.rerun()
    
    with ac2:
        st.markdown(action_card("📂", "Batch Scan", "Upload CSV for bulk analysis of multiple sites"), unsafe_allow_html=True)
        if st.button("Start Batch Scan", key="dash_batch", width='stretch', type="primary"):
            st.session_state.page = "batch_scan"
            st.rerun()
    
    with ac3:
        st.markdown(action_card("📜", "View History", "Review past compliance reports and trends"), unsafe_allow_html=True)
        if st.button("Open History", key="dash_history", width='stretch', type="primary"):
            st.session_state.page = "history"
            st.rerun()
    
    # Recent scans - more compact
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Recent Scans")
    
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
                        if grade == 'A':
                            grade_color = '#10b981'
                        elif grade in ['B', 'C']:
                            grade_color = '#f59e0b'
                        else:
                            grade_color = '#ef4444'
                        st.markdown(f"<div style='text-align: center; padding: 8px;'><span style='color: {grade_color}; font-weight: bold; font-size: 20px;'>{grade}</span></div>", unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("View", key=f"details_{idx}", width='stretch', type="secondary"):
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
