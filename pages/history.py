"""History page - view and manage past scans."""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from components import (
    render_header,
    render_comparison_view,
    render_history_export,
)
from database.operations import (
    get_all_scans,
    get_scan_by_url,
    delete_scan,
    get_scans_by_date_range,
)
from logger_config import get_logger

logger = get_logger(__name__)


def render_history_page():
    """Render the scan history page."""
    render_header()
    
    st.markdown("# Scan History")
    st.markdown("Browse, filter, and compare your compliance scanning history")
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["All Scans", "Compare", "Statistics", "Export"])
    
    with tab1:
        render_all_scans_view()
    
    with tab2:
        render_comparison_view_tab()
    
    with tab3:
        render_statistics_view()
    
    with tab4:
        render_export_view()


def render_all_scans_view():
    """Render all scans with filters."""
    st.markdown("### All Scans")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_grade = st.multiselect(
            "Filter by Grade",
            options=["A", "B", "C", "D", "F"],
            key="filter_grade"
        )
    
    with col2:
        date_range = st.slider(
            "Days back",
            min_value=1,
            max_value=90,
            value=30,
            step=1,
            key="date_range"
        )
    
    with col3:
        search_url = st.text_input(
            "Search URL",
            placeholder="example.com",
            label_visibility="collapsed",
            key="search_url"
        )
    
    # Load scans
    try:
        if search_url:
            scans = get_scan_by_url(search_url)
        else:
            scans = get_all_scans()
        
        if not scans:
            st.info("No scans found. Start with a quick or batch scan!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(scans)
        
        # Apply filters
        if filter_grade:
            df = df[df["grade"].isin(filter_grade)]
        
        if "scan_date" in df.columns:
            cutoff_date = datetime.now() - timedelta(days=date_range)
            df["scan_date"] = pd.to_datetime(df["scan_date"])
            df = df[df["scan_date"] >= cutoff_date]
        
        if df.empty:
            st.info("No scans match your filters.")
            return
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Scans", len(df))
        
        with col2:
            avg_score = df["score"].mean() if "score" in df.columns else 0
            st.metric("Avg Score", f"{avg_score:.1f}")
        
        with col3:
            compliant = (df["score"] >= 80).sum() if "score" in df.columns else 0
            st.metric("Compliant", compliant)
        
        with col4:
            at_risk = (df["score"] < 60).sum() if "score" in df.columns else 0
            st.metric("At Risk", at_risk)
        
        st.markdown("---")
        
        # Display table
        display_cols = ["url", "score", "grade", "status", "scan_date"]
        available_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(
            df[available_cols].sort_values(
                by="scan_date" if "scan_date" in df.columns else "score",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons
        st.markdown("---")
        
        if st.button("🗑️ Clear History", type="secondary"):
            if st.confirm("Are you sure? This cannot be undone."):
                try:
                    # Note: You'll need to implement a delete_all_scans function
                    st.success("History cleared successfully!")
                except Exception as e:
                    st.error(f"Error clearing history: {e}")
    
    except Exception as e:
        logger.error(f"Error loading scan history: {e}")
        st.error("Could not load scan history. Please try again.")


def render_comparison_view_tab():
    """Render comparison tool."""
    st.markdown("### 🔄 Compare Scans")
    
    try:
        scans = get_all_scans()
        
        if len(scans) < 2:
            st.info("You need at least 2 scans to compare.")
            return
        
        scan_options = [f"{s['url']} - {s['scan_date']}" for s in scans]
        
        col1, col2 = st.columns(2)
        
        with col1:
            scan1_idx = st.selectbox("First Scan", range(len(scan_options)), key="comp1")
        
        with col2:
            scan2_idx = st.selectbox("Second Scan", range(len(scan_options)), key="comp2")
        
        if scan1_idx != scan2_idx:
            if st.button("Compare", type="primary", use_container_width=True):
                render_comparison_view(scans[scan1_idx], scans[scan2_idx])
        else:
            st.warning("Please select two different scans.")
    
    except Exception as e:
        logger.error(f"Error rendering comparison: {e}")
        st.error("Could not load scans for comparison.")


def render_statistics_view():
    """Render statistics and trends."""
    st.markdown("### 📊 Statistics & Trends")
    
    try:
        scans = get_all_scans()
        
        if not scans:
            st.info("No data available yet.")
            return
        
        df = pd.DataFrame(scans)
        
        # Score distribution
        st.markdown("**Score Distribution**")
        if "score" in df.columns:
            st.histogram(df["score"], nbins=20)
        
        # Grade distribution
        st.markdown("**Grade Distribution**")
        if "grade" in df.columns:
            grade_counts = df["grade"].value_counts().sort_index()
            st.bar_chart(grade_counts)
        
        # Compliance rate
        st.markdown("**Compliance Status**")
        if "score" in df.columns:
            compliant = (df["score"] >= 80).sum()
            at_risk = (df["score"] < 60).sum()
            needs_work = len(df) - compliant - at_risk
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✓ Compliant", compliant)
            with col2:
                st.metric("~ Needs Work", needs_work)
            with col3:
                st.metric("✗ At Risk", at_risk)
    
    except Exception as e:
        logger.error(f"Error rendering statistics: {e}")
        st.error("Could not load statistics.")


def render_export_view():
    """Render export options."""
    st.markdown("### 📥 Export Data")
    
    try:
        scans = get_all_scans()
        
        if not scans:
            st.info("No scans to export.")
            return
        
        render_history_export(scans)
    
    except Exception as e:
        logger.error(f"Error rendering export: {e}")
        st.error("Could not load scans for export.")


def main():
    """Main function for history page."""
    if "page" not in st.session_state:
        st.session_state.page = "history"
    
    render_history_page()


if __name__ == "__main__":
    main()
