"""Quick Scan page - single URL scanning."""

import html as html_module
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
from libs.cache import get_scan_cache
from libs.rate_limit import check_scan_rate_limit
from services.openai_service import OpenAIService
from exceptions import ScanError, NetworkError
from logger_config import get_logger
from config import Config

logger = get_logger(__name__)

# Use the module-level singleton so cache is shared across pages
scan_cache = get_scan_cache()


def render_quick_scan_page():
    """Render the quick scan page."""
    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon amber">⚡</div>
  <div>
    <h1 class="page-hero-title">Quick Scan</h1>
    <p class="page-hero-subtitle">Instantly analyze any website for GDPR &amp; CCPA compliance &mdash; cookie consent, privacy policy, trackers &amp; more</p>
  </div>
</div>
""", unsafe_allow_html=True)

    url, submitted = render_scan_form()

    # AI analysis toggle — shown in a styled card below the form
    ai_enabled = False
    if Config.OPENAI_API_KEY:
        st.markdown('<div class="ai-toggle-card"><span class="ai-toggle-badge">✦ Optional</span>', unsafe_allow_html=True)
        ai_enabled = st.toggle(
            "Enable AI Analysis",
            value=False,
            help="After scanning, fetches the site's privacy policy and analyzes it with GPT",
        )
        st.markdown('</div>', unsafe_allow_html=True)
    if submitted:
        is_valid, prepared_url, error_msg = validate_and_prepare_url(url)

        if not is_valid:
            st.error(error_msg)
            return

        # Rate limit check (cached results bypass the limit — no new network request)
        cached_result = scan_cache.get(prepared_url)

        if not cached_result:
            allowed, rate_msg = check_scan_rate_limit(Config.SCAN_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                st.warning(rate_msg)
                return

        # If cached but AI was requested and not yet run, top up with AI analysis
        if cached_result and ai_enabled and not cached_result.get("ai_analysis"):
            with st.spinner("Running AI analysis on privacy policy..."):
                try:
                    svc = OpenAIService()
                    cached_result["ai_analysis"] = svc.analyze_privacy_policy(prepared_url, cached_result)
                    scan_cache.set(prepared_url, cached_result)
                    try:
                        from database.operations import save_scan_result
                        save_scan_result(prepared_url, cached_result, cached_result["ai_analysis"])
                    except Exception as db_error:
                        logger.warning(f"Database update failed: {db_error}")
                except Exception as e:
                    logger.warning(f"AI analysis failed: {e}")

        if cached_result:
            _render_success_banner(prepared_url, cached_result, cached=True)
            render_scan_results(cached_result)
        else:
            try:
                with st.status("Scanning website...", expanded=True) as status:
                    st.write("Fetching page content...")
                    controller = ComplianceController()

                    st.write("Analyzing cookies, privacy policy & contact info...")
                    result = controller.scan_website(prepared_url)

                    st.write("Calculating compliance score...")
                    result["scan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result["url"] = prepared_url

                    if ai_enabled:
                        st.write("Running AI analysis on privacy policy...")
                        try:
                            svc = OpenAIService()
                            result["ai_analysis"] = svc.analyze_privacy_policy(prepared_url, result)
                        except Exception as e:
                            logger.warning(f"AI analysis failed: {e}")
                            result["ai_analysis"] = None

                    status.update(label="Scan complete", state="complete", expanded=False)

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

            scan_cache.set(prepared_url, result)

            try:
                from database.operations import save_scan_result
                save_scan_result(prepared_url, result, result.get("ai_analysis"))
            except Exception as db_error:
                logger.warning(f"Database save failed: {db_error}")

            score = result.get("score", 0)
            grade = result.get("grade", "F")
            st.toast(f"Scan complete — Score {score}/100, Grade {grade}", icon="✅")

            _render_success_banner(prepared_url, result)
            render_scan_results(result)


def _render_success_banner(url: str, result: dict, cached: bool = False):
    """Render a rich scan-complete banner with inline score + grade."""
    score = result.get("score", 0)
    grade = result.get("grade", "F")
    color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
    cached_tag = ' <span style="opacity:0.55;font-size:0.8em;">(cached)</span>' if cached else ""
    st.markdown(f"""
<div class="scan-success-banner">
  <span class="scan-success-icon">&#10003;</span>
  <div class="scan-success-text">
    <strong>Scan complete</strong>{cached_tag} &mdash; {html_module.escape(url)}
  </div>
  <div class="scan-success-score" style="color:{color};">{score}/100 &nbsp;&nbsp; Grade&nbsp;{html_module.escape(grade)}</div>
</div>
""", unsafe_allow_html=True)


def render_scan_results(result: dict):
    """Render detailed scan results."""
    # Score hero card + category breakdown (no plain ## Results heading needed)
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
        st.markdown("---")
        render_ai_analysis(result["ai_analysis"])

    # ── Remediation advice (AI-powered, on demand) ─────────────────────────
    if Config.OPENAI_API_KEY and result.get("score", 100) < 100:
        st.markdown("---")
        _render_remediation_advice(result)

    # Export options (at the end)
    st.markdown("---")
    render_export_options(result)


def _render_remediation_advice(result: dict):
    """
    Render an on-demand AI remediation advice panel.

    Fetches advice once per URL and caches it in st.session_state so it
    survives reruns without triggering extra API calls.
    """
    url = result.get("url", "")
    cache_key = f"_remediation_{url}"

    st.markdown("#### AI Remediation Advice")

    existing = st.session_state.get(cache_key)

    if existing:
        with st.expander("View Remediation Advice", expanded=True):
            st.markdown(existing)
    else:
        if st.button(
            "Get AI Remediation Advice",
            key=f"remediation_btn_{url}",
            help="Uses GPT to generate prioritised fix steps for each failing compliance check",
        ):
            with st.spinner("Generating remediation advice..."):
                try:
                    svc = OpenAIService()
                    advice = svc.get_remediation_advice(result)
                    st.session_state[cache_key] = advice or "No advice available."
                    st.rerun()
                except Exception as e:
                    logger.warning(f"Remediation advice failed: {e}")
                    st.error("Could not generate remediation advice. Please try again.")


def main():
    """Main function for quick scan page."""
    if "page" not in st.session_state:
        st.session_state.page = "quick_scan"

    render_quick_scan_page()


if __name__ == "__main__":
    main()
