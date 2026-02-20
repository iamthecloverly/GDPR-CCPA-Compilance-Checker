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
    
    # Scoring explanation
    with st.expander("ℹ️ How Scoring Works", expanded=False):
        st.markdown("""
        ### Compliance Score Breakdown (0-100 points)
        
        | Category | Max Points | Description |
        |----------|------------|-------------|
        | **Cookie Consent** | 30 | Banner or mechanism for users to manage cookies |
        | **Privacy Policy** | 30 | Clear and accessible privacy policy document |
        | **Contact Information** | 20 | DPO/Privacy contact details available |
        | **Tracker Management** | 20 | Bonus for minimal third-party trackers |
        
        ### Grade Scale
        - **A (90-100)**: Excellent compliance
        - **B (80-89)**: Good compliance  
        - **C (70-79)**: Acceptable compliance
        - **D (60-69)**: Needs improvement
        - **F (<60)**: Non-compliant
        
        ### Status Categories
        - **Compliant**: Score ≥ 80 points
        - **Needs Improvement**: Score 60-79 points
        - **Non-Compliant**: Score < 60 points
        """)
    
    st.markdown("---")
    
    # Quick comparison table
    if completed_items:
        with st.expander("📊 Quick Comparison Table", expanded=True):
            st.markdown("*Click on any row below for detailed analysis*")
            
            # Create comparison dataframe
            comparison_data = []
            for item in completed_items:
                comparison_data.append({
                    "Website": item.get("url", "Unknown"),
                    "Score": item.get("score", 0),
                    "Grade": item.get("grade", "F"),
                    "Status": item.get("status", "Unknown"),
                    "Cookie Consent": "✅" if "Found" in str(item.get("cookie_consent", "")) else "❌",
                    "Privacy Policy": "✅" if "Found" in str(item.get("privacy_policy", "")) else "❌",
                    "Trackers": len(item.get("trackers", []))
                })
            
            df = pd.DataFrame(comparison_data)
            df = df.sort_values("Score", ascending=False)
            
            # Style the dataframe
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
    
    st.markdown("---")
    
    # Detailed Results by Site
    if completed_items:
        st.subheader("🔍 Detailed Site Analysis")
        st.caption("Expand each site for comprehensive compliance breakdown and AI insights")
        
        # Sort by score (highest first)
        sorted_items = sorted(completed_items, key=lambda x: x.get("score", 0), reverse=True)
        
        for idx, item in enumerate(sorted_items, 1):
            render_site_detailed_result(item, idx)
    
    if failed_items:
        st.markdown("---")
        with st.expander(f"❌ Failed URLs ({len(failed_items)})", expanded=False):
            for url in failed_items:
                st.error(f"• {url}")


def render_site_detailed_result(result: Dict[str, Any], index: int):
    """
    Render detailed result for a single site with scoring breakdown and AI analysis.
    
    Args:
        result: Scan result dictionary
        index: Site index number
    """
    url = result.get("url", "Unknown")
    score = result.get("score", 0)
    grade = result.get("grade", "F")
    status = result.get("status", "Unknown")
    
    # Color coding based on grade
    grade_colors = {
        "A": "🟢",
        "B": "🟢",
        "C": "🟡",
        "D": "🟠",
        "F": "🔴"
    }
    grade_icon = grade_colors.get(grade, "⚪")
    
    # Status emoji
    status_emoji = {
        "Compliant": "✅",
        "Needs Improvement": "⚠️",
        "Non-Compliant": "❌"
    }
    status_icon = status_emoji.get(status, "❓")
    
    with st.expander(f"{grade_icon} **#{index}. {url}** • {score}/100 • Grade {grade} {status_icon}", expanded=False):
        # Top-level summary
        st.markdown(f"### {status_icon} {status}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Score", f"{score}/100", delta=None)
        
        with col2:
            st.metric("Grade", grade)
        
        with col3:
            trackers_count = len(result.get("trackers", []))
            delta_text = "Good" if trackers_count == 0 else f"-{trackers_count}"
            st.metric("Trackers", trackers_count, delta=delta_text, delta_color="inverse")
        
        with col4:
            scan_date = result.get("scan_date", "N/A")
            if scan_date != "N/A":
                scan_date = scan_date.split()[0]  # Just the date
            st.metric("Scan Date", scan_date)
        
        st.markdown("---")
        
        # Score breakdown in dropdown
        with st.expander("📊 Score Breakdown by Category", expanded=False):
            score_breakdown = result.get("score_breakdown", {})
            
            if score_breakdown:
                # Create visual score breakdown
                for category, points in score_breakdown.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{category}**")
                    with col2:
                        # Determine max points by category
                        max_points = {
                            "Cookie Consent": 30,
                            "Privacy Policy": 30,
                            "Contact Info": 20
                        }
                        category_key = next((k for k in max_points if k in category), None)
                        max_val = max_points.get(category_key, 20)
                        
                        if "Trackers" in category:
                            # For trackers, show differently
                            st.markdown(f"**{points}** pts")
                        else:
                            st.markdown(f"**{points}/{max_val}** pts")
                    
                    # Progress bar for visualization
                    if "Trackers" not in category:
                        progress = points / max_val if max_val > 0 else 0
                        st.progress(progress)
                    else:
                        # For trackers, show inverse (less is better)
                        if points > 0:
                            st.progress(1.0)  # Full bar if got points
                        else:
                            st.progress(0.0)
            else:
                st.info("Score breakdown not available")
        
        # Compliance findings in dropdown
        with st.expander("🔍 Compliance Findings", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🍪 Cookie Consent")
                cookie_status = result.get("cookie_consent", "Not Found")
                if "Found" in str(cookie_status):
                    st.success(f"✅ {cookie_status}")
                else:
                    st.error(f"❌ {cookie_status}")
                
                st.markdown("#### 📄 Privacy Policy")
                policy_status = result.get("privacy_policy", "Not Found")
                if "Found" in str(policy_status):
                    st.success(f"✅ {policy_status}")
                else:
                    st.error(f"❌ {policy_status}")
            
            with col2:
                st.markdown("#### 📧 Contact Information")
                contact_status = result.get("contact_info", "Not Found")
                if "Found" in str(contact_status):
                    st.success(f"✅ {contact_status}")
                else:
                    st.warning(f"⚠️ {contact_status}")
                
                st.markdown("#### 🎯 Third-Party Trackers")
                trackers = result.get("trackers", [])
                if trackers:
                    st.warning(f"⚠️ {len(trackers)} tracker(s) detected")
                else:
                    st.success("✅ No trackers detected")
            
            # Show tracker details if any
            if trackers:
                with st.expander(f"📋 View all {len(trackers)} tracker(s)", expanded=False):
                    tracker_cols = st.columns(2)
                    for i, tracker in enumerate(trackers):
                        with tracker_cols[i % 2]:
                            st.text(f"• {tracker}")
        
        # AI Analysis in dropdown
        ai_analysis = result.get("ai_analysis")
        if ai_analysis:
            with st.expander("🤖 AI Compliance Analysis", expanded=False):
                st.markdown(ai_analysis)
        else:
            with st.expander("🤖 AI Compliance Analysis", expanded=False):
                st.info("AI analysis is being generated or not available for this scan.")
        
        # Recommendations in dropdown
        recommendations = result.get("recommendations", [])
        if recommendations:
            with st.expander(f"💡 Recommendations ({len(recommendations)})", expanded=False):
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
        
        # Additional details in dropdown
        findings = result.get("findings", {})
        if findings:
            with st.expander("📝 Additional Details", expanded=False):
                for key, value in findings.items():
                    if value:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
