# IMPROVED APP STRUCTURE EXAMPLE
# This shows how to refactor app.py for better maintainability

# ============================================================================
# FILE: components/header.py - Reusable header component
# ============================================================================

import streamlit as st

def render_header():
    """Render consistent header with logo and navigation"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("🔒")  # Logo
    
    with col2:
        st.markdown("""
        <h1 style=\"font-size: 28px; margin: 0;\">
            Compliance Checker
        </h1>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("⚙️ Settings", key="header_settings"):
            st.session_state["page"] = "settings"


def render_stats_row(stats: dict):
    """Render a row of stat cards
    
    Args:
        stats: Dict with keys: total_scans, avg_score, compliant_count
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Scans", stats["total_scans"], "scans")
    
    with col2:
        st.metric("Avg Score", f\"{stats['avg_score']:.0f}\", "/ 100")
    
    with col3:
        st.metric("Compliant Sites", stats["compliant_count"], "sites")


# ============================================================================
# FILE: components/scan_form.py - Improved scan input with validation
# ============================================================================

import streamlit as st
from validators import validate_url, InvalidURLError

def render_scan_form() -> tuple[str, bool]:
    \"\"\"
    Render improved scan form with validation
    
    Returns:
        (url: str, submitted: bool)
    \"\"\"
    st.subheader("🔍 Enter URL to Scan")
    st.caption("Paste the domain you want to analyze for compliance issues")
    
    with st.form("scan_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            url = st.text_input(
                label="Website URL",
                placeholder="https://example.com",
                help="Enter complete URL with protocol",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button(
                "🔍 Scan",
                use_container_width=True,
                type="primary"
            )
    
    return url, submitted


def validate_and_prepare_url(raw_url: str) -> tuple[bool, str, str]:
    \"\"\"
    Validate URL and return (is_valid, url, error_message)
    
    Args:
        raw_url: User input URL string
        
    Returns:
        Tuple of (is_valid, prepared_url, error_message)
    \"\"\"
    if not raw_url or not raw_url.strip():
        return False, "", "Please enter a website URL"
    
    try:
        is_valid, url = validate_url(raw_url)
        if not is_valid:
            return False, "", f"Invalid URL format: {raw_url}"
        return True, url, ""
    except InvalidURLError as e:
        return False, "", f"URL validation failed: {str(e)}"
    except Exception as e:
        return False, "", f"Error processing URL: {str(e)}"


# ============================================================================
# FILE: components/results_display.py - Better results visualization
# ============================================================================

import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_quick_results(results: Dict[str, Any]):
    \"\"\"
    Render quick results with improved layout
    
    Args:
        results: Scan results dictionary
    \"\"\"
    # Use columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Large score display
        score = results.get("score", 0)
        grade = results.get("grade", "F")
        
        # Color based on score
        if score >= 80:
            color = "#22c55e"
        elif score >= 60:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        st.markdown(f\"\"\"
        <div style=\"text-align: center; padding: 20px;\">
            <div style=\"font-size: 64px; font-weight: bold; color: {color};\">
                {score}
            </div>
            <div style=\"font-size: 24px; color: {color}; margin-top: 10px;\">
                Grade: <span style=\"background: {color}30; padding: 4px 12px; border-radius: 8px;\">{grade}</span>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
    
    with col2:
        # Score breakdown chart
        breakdown = results.get("breakdown", [])
        if breakdown:
            df = pd.DataFrame(breakdown)
            
            st.markdown("**Score Breakdown:**")
            for _, row in df.iterrows():
                st.markdown(f\"\"\"
                {row['Category']}: **{row['Points']} points** {'✓' if row['Points'] > 0 else '✗'}
                \"\"\")
    
    with col3:
        # Quick findings
        st.markdown("**Status:**")
        st.markdown(f\"\"\"
        • {results.get('status', 'Unknown')}
        • Trackers: {len(results.get('trackers', []))}
        • Privacy Policy: {'Found' if 'Found' in results.get('privacy_policy', '') else 'Missing'}
        \"\"\")


def render_detailed_results(results: Dict[str, Any]):
    \"\"\"
    Render detailed expandable results
    
    Args:
        results: Full scan results
    \"\"\"
    with st.expander("📊 Detailed Results", expanded=True):
        # Cookie Consent Analysis
        with st.expander("🍪 Cookie Consent"):
            cookie_status = results.get("cookie_consent", "Not Found")
            st.write(f\"Status: {cookie_status}\")
            if "Found" in cookie_status:
                st.success("✓ Cookie consent banner detected")
            else:
                st.warning("✗ No cookie consent found")
        
        # Privacy Policy
        with st.expander("📄 Privacy Policy"):
            privacy_status = results.get("privacy_policy", "Not Found")
            st.write(f\"Status: {privacy_status}\")
        
        # Contact Information
        with st.expander("📧 Contact Information"):
            contact_status = results.get("contact_info", "Not Found")
            st.write(f\"Status: {contact_status}\")
        
        # Trackers
        with st.expander(f\"📍 Trackers ({len(results.get('trackers', []))})\"):
            trackers = results.get("trackers", [])
            if trackers:
                st.write(f\"Found {len(trackers)} tracking domains:\")
                for tracker in trackers[:10]:  # Show first 10
                    st.code(tracker)
            else:
                st.success("No trackers detected")


# ============================================================================
# FILE: pages/dashboard.py (Simplified version of main app)
# ============================================================================

import streamlit as st
from components.header import render_header, render_stats_row
from components.scan_form import render_scan_form, validate_and_prepare_url

def main_dashboard():
    \"\"\"Main dashboard page\"\"\"
    
    # Render header
    render_header()
    
    st.markdown(\"---\")
    
    # Hero section
    st.markdown(\"\"\"
    ## 🚀 Quick Scan
    
    Scan any website in seconds to check for GDPR/CCPA compliance signals
    \"\"\")
    
    # Scan form
    url, submitted = render_scan_form()
    
    if submitted:
        is_valid, prepared_url, error_msg = validate_and_prepare_url(url)
        
        if not is_valid:
            st.error(error_msg)
        else:
            # Perform scan
            with st.spinner("🔍 Scanning website..."):
                try:
                    from controllers.compliance_controller import ComplianceController
                    controller = ComplianceController()
                    results = controller.scan_website(prepared_url)
                    
                    # Display results
                    render_quick_results(results)
                    render_detailed_results(results)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.button("📥 Download Report")
                    with col2:
                        st.button("📊 View Details")
                    with col3:
                        st.button("➕ Scan Another")
                    
                except Exception as e:
                    st.error(f\"Scan failed: {str(e)}\")
    
    st.markdown(\"---\")
    
    # Show recent scans
    st.subheader(\"Recent Scans\")
    st.caption(\"Your past compliance checks\")
    
    # Placeholder for recent scans table


if __name__ == \"__main__\":
    main_dashboard()


# ============================================================================
# FILE: utils/formatters.py - Formatting utilities
# ============================================================================

from datetime import datetime
from typing import Union

def format_score(score: Union[int, float]) -> str:
    \"\"\"Format score with color\"\"\"
    if score >= 80:
        color = \"green\"
    elif score >= 60:
        color = \"orange\"
    else:
        color = \"red\"
    return f\":{color}[{score:.0f}]\"


def format_date(date: datetime) -> str:
    \"\"\"Format date in readable format\"\"\"
    return date.strftime(\"%b %d, %Y\")


def format_tracker_count(count: int) -> str:
    \"\"\"Format tracker count with status\"\"\"
    if count == 0:
        return \"✓ No trackers\"
    elif count <= 3:
        return f\"⚠️ {count} trackers\"
    else:
        return f\"🔴 {count} trackers\"


# ============================================================================
# FILE: utils/export.py - Export utilities
# ============================================================================

import csv
from io import StringIO
from typing import List, Dict, Any

def create_csv_export(scans: List[Dict[str, Any]]) -> str:
    \"\"\"
    Create CSV export from scan results
    
    Args:
        scans: List of scan result dictionaries
        
    Returns:
        CSV string ready for download
    \"\"\"
    output = StringIO()
    
    if not scans:
        return \"\"
    
    fieldnames = [\"URL\", \"Score\", \"Grade\", \"Status\", \"Date\", \"Trackers\"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for scan in scans:
        writer.writerow({
            \"URL\": scan.get(\"url\", \"\"),
            \"Score\": scan.get(\"score\", 0),
            \"Grade\": scan.get(\"grade\", \"F\"),
            \"Status\": scan.get(\"status\", \"Unknown\"),
            \"Date\": scan.get(\"date\", \"\"),
            \"Trackers\": len(scan.get(\"trackers\", []))
        })
    
    return output.getvalue()


# ============================================================================
# Benefits of this structure:
# ============================================================================
# 1. ✓ Reusable components - Use header.py in multiple pages
# 2. ✓ Better organization - Separate concerns into different files
# 3. ✓ Easier testing - Can test components independently
# 4. ✓ Cleaner main app.py - Only 100 lines instead of 783
# 5. ✓ Maintainable - Easy to find and update specific functionality
# 6. ✓ Scalable - Easy to add new pages/features
# 7. ✓ Better type hints - Easier to understand function signatures
# 8. ✓ Documentation - Self-documenting code structure
# ============================================================================

