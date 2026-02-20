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
    render_ai_analysis,
)
from controllers.compliance_controller import ComplianceController
from libs.cache import ScanCache
from exceptions import ScanError, NetworkError
from logger_config import get_logger
from config import Config

logger = get_logger(__name__)

# Initialize cache
scan_cache = ScanCache(ttl_hours=24, max_items=Config.CACHE_MAXSIZE)


def render_quick_scan_page():
    """Render the quick scan page."""
    st.markdown("# Quick Scan")
    st.markdown("Analyze a single website for GDPR and CCPA compliance")

    # AI analysis toggle
    ai_enabled = False
    if Config.OPENAI_API_KEY:
        ai_enabled = st.toggle(
            "Enable AI Analysis",
            value=False,
            help="After scanning, fetches the site's privacy policy and analyzes it with GPT",
        )
    else:
        st.caption("AI analysis unavailable — set OPENAI_API_KEY to enable")

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
            try:
                with st.spinner("Scanning website..."):
                    controller = ComplianceController()
                    result = controller.scan_website(prepared_url)

                    result["scan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result["url"] = prepared_url

            except NetworkError as e:
                st.error(f"**Could not reach the website:** {e}")
                st.info(
                    "**Troubleshooting tips:**\n"
                    "- Double-check the URL spelling\n"
                    "- Make sure the site is publicly accessible (not behind a login or VPN)\n"
                    "- Try opening the URL in your browser first"
                )
                return
            except ScanError as e:
                st.error(f"**Scan failed:** {e}")
                st.info("If this is unexpected, try again or verify the site is accessible in a browser.")
                return
            except Exception as e:
                logger.error(f"Unhandled scan error for {prepared_url}: {e}")
                st.error("**An unexpected error occurred.** Please try again.")
                return

            if ai_enabled:
                with st.spinner("Running AI analysis on privacy policy..."):
                    try:
                        from services.openai_service import OpenAIService
                        svc = OpenAIService()
                        result["ai_analysis"] = svc.analyze_privacy_policy(prepared_url, result)
                    except Exception as e:
                        logger.warning(f"AI analysis failed: {e}")
                        result["ai_analysis"] = None

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
    st.markdown("## Results")

    # Score, chart, and summary
    render_quick_results(result)

    # Detailed findings
    findings = result.get("findings", {})
    if findings:
        st.markdown("---")  # Visual separator for clean layout
        render_findings(findings)

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        st.markdown("---")  # Visual separator for clean layout
        render_recommendations(recommendations)

    # AI analysis (shown if available)
    if result.get("ai_analysis"):
        st.markdown("---")  # Visual separator for clean layout
        render_ai_analysis(result["ai_analysis"])

    # Export options (at the end after AI analysis)
    st.markdown("---")  # Visual separator before export section
    render_export_options(result)


def main():
    """Main function for quick scan page."""
    if "page" not in st.session_state:
        st.session_state.page = "quick_scan"

    render_quick_scan_page()


if __name__ == "__main__":
    main()
