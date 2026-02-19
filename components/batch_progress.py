"""Batch operations progress tracking components."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd


def render_batch_progress(
    current: int,
    total: int,
    stage: str = "",
    completed_items: List[Dict[str, Any]] = None,
    failed_items: List[str] = None
):
    """
    Render progress bar and status for batch operations.
    
    Args:
        current: Current item index
        total: Total items to process
        stage: Current operation stage
        completed_items: List of completed scan results
        failed_items: List of failed URLs
    """
    completed_items = completed_items or []
    failed_items = failed_items or []
    
    # Progress bar
    progress_value = current / total if total > 0 else 0
    percentage = int(progress_value * 100)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.progress(progress_value, text=f"{percentage}% Complete")
    
    with col2:
        st.markdown(f"**{current} / {total}**")
    
    # Status information
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Completed", len(completed_items), "scans")
    
    with col2:
        st.metric("Failed", len(failed_items), "URLs")
    
    with col3:
        st.metric("Pending", total - current, "items")
    
    with col4:
        st.metric("Current Stage", stage[:15] or "Ready")
    
    # Expandable sections for results
    st.markdown("---")
    
    if completed_items:
        with st.expander(f"✓ Completed ({len(completed_items)})", expanded=False):
            df_completed = pd.DataFrame(completed_items)
            if "url" in df_completed.columns and "score" in df_completed.columns:
                display_cols = ["url", "score", "grade"]
                available_cols = [c for c in display_cols if c in df_completed.columns]
                st.dataframe(
                    df_completed[available_cols],
                    width='stretch',
                    hide_index=True
                )
            else:
                st.write(df_completed)
    
    if failed_items:
        with st.expander(f"✗ Failed ({len(failed_items)})", expanded=False):
            for url in failed_items:
                st.error(f"❌ {url}")


def render_batch_summary(
    completed_items: List[Dict[str, Any]],
    failed_items: List[str]
):
    """
    Render summary of batch scan results.
    
    Args:
        completed_items: List of completed scan results
        failed_items: List of failed URLs
    """
    total = len(completed_items) + len(failed_items)
    success_rate = (len(completed_items) / total * 100) if total > 0 else 0
    
    st.markdown("## 📊 Batch Scan Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scanned", total)
    
    with col2:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col3:
        if completed_items:
            avg_score = sum(item.get("score", 0) for item in completed_items) / len(completed_items)
            st.metric("Avg Score", f"{avg_score:.1f}", "/100")
        else:
            st.metric("Avg Score", "N/A")
    
    with col4:
        compliant_count = sum(1 for item in completed_items if item.get("score", 0) >= 80)
        st.metric("Compliant Sites", compliant_count)
    
    st.markdown("---")
    
    # Results table
    if completed_items:
        st.subheader("✓ Detailed Results")
        df = pd.DataFrame(completed_items)
        
        # Select relevant columns
        display_cols = ["url", "score", "grade", "status"]
        available_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(
            df[available_cols],
            width='stretch',
            hide_index=True
        )
    
    if failed_items:
        st.subheader("✗ Failed URLs")
        for url in failed_items:
            st.error(url)
