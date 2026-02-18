"""Comparison tool components for side-by-side scan comparison."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd


def render_comparison_view(scan1: Dict[str, Any], scan2: Dict[str, Any]):
    """
    Render side-by-side comparison of two scans.
    
    Args:
        scan1: First scan result dictionary
        scan2: Second scan result dictionary
    """
    st.markdown("## 📊 Scan Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {scan1.get('url', 'Scan 1')}")
        render_scan_comparison_card(scan1)
    
    with col2:
        st.markdown(f"### {scan2.get('url', 'Scan 2')}")
        render_scan_comparison_card(scan2)
    
    # Difference analysis
    st.markdown("---")
    st.markdown("### 📈 Differences")
    
    score_diff = scan2.get("score", 0) - scan1.get("score", 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if score_diff > 0:
            st.metric("Score Change", f"+{score_diff}", delta=f"{score_diff:+.1f}")
        elif score_diff < 0:
            st.metric("Score Change", f"{score_diff}", delta=f"{score_diff:+.1f}")
        else:
            st.metric("Score Change", "No change", "0")
    
    with col2:
        grade1 = scan1.get("grade", "N/A")
        grade2 = scan2.get("grade", "N/A")
        if grade1 != grade2:
            st.warning(f"Grade changed: {grade1} → {grade2}")
        else:
            st.success(f"Grade unchanged: {grade1}")
    
    with col3:
        status1 = scan1.get("status", "Unknown")
        status2 = scan2.get("status", "Unknown")
        if status1 != status2:
            st.info(f"Status: {status1} → {status2}")
        else:
            st.success(f"Status: {status1}")
    
    # Detailed comparison
    render_findings_comparison(
        scan1.get("findings", {}),
        scan2.get("findings", {})
    )


def render_scan_comparison_card(scan: Dict[str, Any]):
    """Render a comparison card for a single scan."""
    score = scan.get("score", 0)
    
    if score >= 80:
        color = "#22c55e"
    elif score >= 60:
        color = "#f59e0b"
    else:
        color = "#ef4444"
    
    card_html = f"""
    <div style="background: rgba(30, 33, 46, 0.5); padding: 20px; border-radius: 12px; text-align: center;">
        <div style="font-size: 48px; font-weight: bold; color: {color};">
            {score}
        </div>
        <div style="font-size: 12px; color: #a0aec0; margin-top: 5px;">/ 100</div>
        <div style="font-size: 18px; color: {color}; margin-top: 10px; font-weight: bold;">
            {scan.get("grade", "F")}
        </div>
        <div style="font-size: 12px; color: #e6edf3; margin-top: 10px;">
            {scan.get("status", "Unknown")}
        </div>
        <div style="font-size: 11px; color: #718096; margin-top: 15px;">
            {scan.get("scan_date", "N/A")}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_findings_comparison(findings1: Dict[str, list], findings2: Dict[str, list]):
    """Compare findings between two scans."""
    st.markdown("### 📋 Findings Comparison")
    
    categories = ["cookie_consent", "privacy_policy", "contact_info", "trackers"]
    
    comparison_data = []
    
    for category in categories:
        items1 = findings1.get(category, [])
        items2 = findings2.get(category, [])
        
        comparison_data.append({
            "Category": category.replace("_", " ").title(),
            "Scan 1": len(items1),
            "Scan 2": len(items2),
            "Change": len(items2) - len(items1)
        })
    
    df = pd.DataFrame(comparison_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Detailed findings
    with st.expander("View Detailed Findings Difference"):
        for category in categories:
            items1 = set(findings1.get(category, []))
            items2 = set(findings2.get(category, []))
            
            removed = items1 - items2
            added = items2 - items1
            unchanged = items1 & items2
            
            if removed or added or unchanged:
                st.markdown(f"#### {category.replace('_', ' ').title()}")
                
                if removed:
                    st.error(f"**Removed ({len(removed)})**")
                    for item in removed:
                        st.write(f"- {item}")
                
                if added:
                    st.success(f"**Added ({len(added)})**")
                    for item in added:
                        st.write(f"- {item}")
                
                if unchanged:
                    st.info(f"**Unchanged ({len(unchanged)})**")
                    for item in unchanged:
                        st.write(f"- {item}")


def render_comparison_selector():
    """Render UI to select two scans for comparison."""
    st.markdown("## 🔄 Select Scans to Compare")
    
    # Will be populated with actual scan history
    scan1_placeholder = st.selectbox(
        "First Scan",
        options=["No scans available"],
        key="compare_scan1"
    )
    
    scan2_placeholder = st.selectbox(
        "Second Scan",
        options=["No scans available"],
        key="compare_scan2"
    )
    
    if st.button("Compare", type="primary"):
        if scan1_placeholder == "No scans available" or scan2_placeholder == "No scans available":
            st.error("Please select two different scans")
        else:
            return scan1_placeholder, scan2_placeholder
    
    return None, None
