"""Batch Scan page - multiple URL scanning."""

import streamlit as st
from datetime import datetime
from components import (
    render_batch_upload_form,
    validate_and_prepare_batch_urls,
    render_batch_summary,
    render_batch_export_options,
)
from controllers.compliance_controller import ComplianceController
from libs.progress import ProgressTracker
from libs.cache import ScanCache
from exceptions import ScanError, NetworkError
from logger_config import get_logger
import traceback

logger = get_logger(__name__)

# Initialize cache
scan_cache = ScanCache(ttl_hours=24)


def render_batch_scan_page():
    """Render the batch scan page."""
    st.markdown("# Batch Scan")
    st.markdown("Upload a CSV and scan multiple websites at once")
    
    csv_content, submitted = render_batch_upload_form()
    
    if submitted:
        # Validate URLs
        is_valid, urls, error_msg = validate_and_prepare_batch_urls(csv_content)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        st.info(f"Ready to scan {len(urls)} website(s)")
        
        if st.button("Start Batch Scanning", type="primary", width='stretch'):
            perform_batch_scan(urls)


def perform_batch_scan(urls: list):
    """
    Perform batch scanning of multiple URLs.
    
    Args:
        urls: List of URLs to scan
    """
    # Initialize tracking
    progress_placeholder = st.empty()
    results_placeholder = st.empty()
    
    controller = ComplianceController()
    progress_tracker = ProgressTracker(total_items=len(urls))
    
    completed_scans = []
    failed_scans = []
    
    # Progress bar container
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        for idx, url in enumerate(urls):
            # Update progress
            progress_tracker.update(
                current=idx,
                stage=f"Scanning {url[:40]}..."
            )
            
            progress_value = (idx + 1) / len(urls)
            progress_bar.progress(progress_value)
            
            with status_text.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Scanning:** {url}")
                with col2:
                    st.markdown(f"`{idx + 1}/{len(urls)}`")
                with col3:
                    st.markdown(f"`{progress_value * 100:.0f}%`")
            
            # Check cache first
            cached_result = scan_cache.get(url)
            
            if cached_result:
                logger.info(f"Using cached result for {url}")
                completed_scans.append(cached_result)
            else:
                # Perform scan
                try:
                    result = controller.scan_website(url)
                    result["scan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result["url"] = url
                    
                    # Cache result
                    scan_cache.set(url, result)
                    
                    # Save to database
                    try:
                        from database.operations import save_scan_result
                        ai_analysis = result.get("ai_analysis")
                        save_scan_result(url, result, ai_analysis)
                    except Exception as db_error:
                        logger.warning(f"Could not save {url} to database: {db_error}")
                    
                    completed_scans.append(result)
                
                except (ScanError, NetworkError) as e:
                    logger.error(f"Scan error for {url}: {e}")
                    failed_scans.append({
                        "url": url,
                        "error": str(e)
                    })
                
                except Exception as e:
                    logger.error(f"Unexpected error scanning {url}: {e}")
                    failed_scans.append({
                        "url": url,
                        "error": f"Unexpected error: {str(e)}"
                    })
        
        # Final progress update
        progress_bar.progress(1.0)
        status_text.empty()
        
        st.success(f"✓ Batch scan completed! Scanned {len(completed_scans)} websites successfully.")
        
        # Show results summary
        st.markdown("---")
        render_batch_summary(completed_scans, [s["url"] for s in failed_scans])
        
        st.markdown("---")
        
        # Export options
        if completed_scans:
            render_batch_export_options(completed_scans)
    
    except Exception as e:
        logger.error(f"Batch scan failed: {e}\n{traceback.format_exc()}")
        st.error(f"⚠️ Batch scan encountered an error: {str(e)}")


def main():
    """Main function for batch scan page."""
    if "page" not in st.session_state:
        st.session_state.page = "batch_scan"
    
    render_batch_scan_page()


if __name__ == "__main__":
    main()
