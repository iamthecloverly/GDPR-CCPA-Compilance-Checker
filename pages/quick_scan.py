"""Quick Scan page - single URL scanning."""

import streamlit as st
from datetime import datetime
from components import (
    render_scan_form,
    validate_and_prepare_url,
    render_quick_results,
    render_findings,
    render_recommendations,
    render_export_options,
)
from controllers.compliance_controller import ComplianceController
from libs.cache import ScanCache
from exceptions import ScanError, NetworkError
from logger_config import get_logger
import traceback

logger = get_logger(__name__)

# Initialize cache
scan_cache = ScanCache(ttl_hours=24)


def render_quick_scan_page():
    """Render the quick scan page."""
    st.markdown("# Quick Scan")
    st.markdown("Analyze a single website for GDPR and CCPA compliance")
    
    url, submitted = render_scan_form()
    
    if submitted:
        is_valid, prepared_url, error_msg = validate_and_prepare_url(url)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        cached_result = scan_cache.get(prepared_url)
        
        if cached_result:
            st.success("Using cached result")
            render_scan_results(cached_result)
        else:
            with st.spinner("🔍 Scanning website..."):
                controller = ComplianceController()
                result = controller.scan_website(prepared_url)
                
                result["scan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result["url"] = prepared_url
                
                scan_cache.set(prepared_url, result)
                
                try:
                    from database.operations import save_scan_result
                    save_scan_result(prepared_url, result, result.get("ai_analysis"))
                except Exception as db_error:
                    logger.warning(f"Database save failed: {db_error}")
                
                st.success("Scan completed!")
                render_scan_results(result)


def render_scan_results(result: dict):
    """Render detailed scan results."""
    st.markdown("---")
    st.markdown("## Results")
    
    # Quick results view
    render_quick_results(result)
    
    st.markdown("---")
    
    # Detailed findings
    findings = result.get("findings", {})
    if findings:
        render_findings(findings)
    
    st.markdown("---")
    
    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        render_recommendations(recommendations)
    
    st.markdown("---")
    
    # Export options
    render_export_options(result)


def main():
    """Main function for quick scan page."""
    if "page" not in st.session_state:
        st.session_state.page = "quick_scan"
    
    render_quick_scan_page()


if __name__ == "__main__":
    main()
