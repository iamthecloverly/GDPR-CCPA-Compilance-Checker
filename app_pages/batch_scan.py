"""Batch Scan page - multiple URL scanning."""

import streamlit as st
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from components import (
    render_batch_upload_form,
    validate_and_prepare_batch_urls,
    render_batch_summary,
    render_batch_export_options,
)
from controllers.compliance_controller import ComplianceController
from libs.progress import ProgressTracker
from libs.cache import get_scan_cache
from libs.rate_limit import check_batch_rate_limit
from services.openai_service import OpenAIService
from exceptions import ScanError, NetworkError
from logger_config import get_logger
from config import Config
logger = get_logger(__name__)

# Use the module-level singleton so cache is shared across pages
scan_cache = get_scan_cache()


def render_batch_scan_page():
    """Render the batch scan page."""
    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon blue">📂</div>
  <div>
    <h1 class="page-hero-title">Batch Scan</h1>
    <p class="page-hero-subtitle">Audit multiple websites at once &mdash; paste a list of URLs or upload a CSV file to get started</p>
  </div>
</div>
""", unsafe_allow_html=True)

    csv_content, submitted = render_batch_upload_form()

    # AI toggle — two-column card: info left, toggle right
    ai_enabled = False
    if Config.OPENAI_API_KEY:
        col_ai_info, col_ai_toggle = st.columns([5, 1])
        with col_ai_info:
            st.markdown("""
<div class="ai-feature-info">
  <span class="ai-feature-icon">🤖</span>
  <div>
    <p class="ai-feature-title">AI Compliance Analysis <span class="ai-feature-badge">Optional</span></p>
    <p class="ai-feature-desc">Runs GPT-powered privacy policy analysis on each site — slower but far more detailed</p>
  </div>
</div>""", unsafe_allow_html=True)
        with col_ai_toggle:
            st.markdown('<div class="ai-toggle-col">', unsafe_allow_html=True)
            ai_enabled = st.toggle(
                "Enable",
                value=False,
                help="After scanning, runs AI privacy-policy analysis on each site (slower but more detailed)",
            )
            st.markdown('</div>', unsafe_allow_html=True)
    if submitted:
        # Validate URLs
        is_valid, urls, error_msg = validate_and_prepare_batch_urls(csv_content)

        if not is_valid:
            st.error(error_msg)
            return

        # Rate limit check for batch scans
        allowed, rate_msg = check_batch_rate_limit(Config.BATCH_RATE_LIMIT_PER_HOUR)
        if not allowed:
            st.warning(rate_msg)
            return

        st.info(f"Starting scan of {len(urls)} website(s)...")
        perform_batch_scan(urls, ai_enabled=ai_enabled)


def perform_batch_scan(urls: list, ai_enabled: bool = False):
    """
    Perform batch scanning of multiple URLs.

    Phase 1 — parallel compliance scans (fast).
    Phase 2 — optional sequential AI analysis, only if ai_enabled=True.

    Args:
        urls: List of URLs to scan.
        ai_enabled: Whether to run AI analysis after scanning completes.
    """
    controller = ComplianceController()
    progress_tracker = ProgressTracker(total_items=len(urls))

    completed_scans: list = []
    failed_scans: list = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # ── Phase 1: Compliance scans ─────────────────────────────────────
        # Track per-URL state for status pills
        url_states: dict = {url: "queued" for url in urls}
        pills_placeholder = st.empty()

        def _render_pills():
            icons = {"queued": "○", "scanning": "●", "done": "✓", "error": "✗"}
            pills = "".join(
                f'<span class="batch-pill {state}">'
                f'<span class="batch-pill-dot"></span>{icons[state]}&nbsp;{u.replace("https://","").replace("http://","")[:30]}'
                f"</span>"
                for u, state in url_states.items()
            )
            pills_placeholder.markdown(
                f'<div class="batch-status-row">{pills}</div>', unsafe_allow_html=True
            )

        _render_pills()

        pending_urls = []
        for url in urls:
            cached = scan_cache.get(url)
            if cached:
                logger.info(f"Using cached result for {url}")
                url_states[url] = "done"
                completed_scans.append(cached)
            else:
                pending_urls.append(url)

        _render_pills()

        processed = len(completed_scans)

        if pending_urls:
            with ThreadPoolExecutor(max_workers=Config.BATCH_MAX_WORKERS) as executor:
                future_to_url = {
                    executor.submit(controller.scan_website, url): url
                    for url in pending_urls
                }

                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    url_states[url] = "scanning"
                    processed += 1
                    progress_tracker.update(current=processed, stage=f"Scanning {url[:40]}...")
                    progress_value = processed / len(urls)
                    progress_bar.progress(progress_value)
                    status_text.markdown(f"`{processed}/{len(urls)}` — scanning `{url[:50]}`")

                    try:
                        result = future.result()
                        result["scan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        result["url"] = url
                        result.setdefault("ai_analysis", None)

                        scan_cache.set(url, result)

                        try:
                            from database.operations import save_scan_result
                            save_scan_result(url, result, None)
                        except Exception as db_err:
                            logger.warning(f"Could not save {url} to database: {db_err}")

                        url_states[url] = "done"
                        completed_scans.append(result)
                    except (ScanError, NetworkError) as e:
                        logger.error(f"Scan error for {url}: {e}")
                        url_states[url] = "error"
                        failed_scans.append({"url": url, "error": str(e)})
                    except Exception as e:
                        logger.error(f"Unexpected error scanning {url}: {e}")
                        url_states[url] = "error"
                        failed_scans.append({"url": url, "error": f"Unexpected error: {str(e)}"})

                    _render_pills()

        progress_bar.progress(1.0)
        status_text.empty()

        # ── Phase 2: AI analysis (optional, sequential) ───────────────────
        if ai_enabled and completed_scans:
            _run_batch_ai_analysis(completed_scans)

        # ── Summary bar ───────────────────────────────────────────────────
        avg_score = (
            sum(s.get("score", 0) for s in completed_scans) / len(completed_scans)
            if completed_scans else 0
        )
        compliant = sum(1 for s in completed_scans if s.get("score", 0) >= 80)
        at_risk   = sum(1 for s in completed_scans if s.get("score", 0) < 60)

        st.markdown(f"""
<div class="batch-summary-bar">
  <div class="batch-summary-item info">
    <span class="batch-summary-val">{len(urls)}</span>
    <span class="batch-summary-lbl">Total</span>
  </div>
  <div class="batch-summary-item success">
    <span class="batch-summary-val">{len(completed_scans)}</span>
    <span class="batch-summary-lbl">Scanned</span>
  </div>
  <div class="batch-summary-item danger">
    <span class="batch-summary-val">{len(failed_scans)}</span>
    <span class="batch-summary-lbl">Failed</span>
  </div>
  <div class="batch-summary-item success">
    <span class="batch-summary-val">{compliant}</span>
    <span class="batch-summary-lbl">Compliant</span>
  </div>
  <div class="batch-summary-item warn">
    <span class="batch-summary-val">{at_risk}</span>
    <span class="batch-summary-lbl">At Risk</span>
  </div>
  <div class="batch-summary-item info">
    <span class="batch-summary-val">{avg_score:.0f}</span>
    <span class="batch-summary-lbl">Avg Score</span>
  </div>
</div>
""", unsafe_allow_html=True)

        st.toast(
            f"Batch scan complete — {len(completed_scans)}/{len(urls)} succeeded, avg score {avg_score:.0f}",
            icon="✅",
        )

        render_batch_summary(completed_scans, [s["url"] for s in failed_scans])

        if completed_scans:
            render_batch_export_options(completed_scans)

    except Exception as e:
        logger.exception(f"Batch scan failed: {type(e).__name__}")
        st.error("Batch scan encountered an error. Please try again or contact support.")


def _run_batch_ai_analysis(scans: list) -> None:
    """
    Run AI privacy-policy analysis sequentially on each completed scan.
    Updates each result dict in-place with 'ai_analysis'.

    Args:
        scans: List of completed scan result dicts (modified in-place).
    """
    svc = OpenAIService()
    total = len(scans)

    st.markdown("**Running AI analysis...**")
    ai_bar = st.progress(0)
    ai_status = st.empty()

    for i, result in enumerate(scans, 1):
        url = result.get("url", "")
        ai_status.markdown(f"Analyzing `{url}` ({i}/{total})...")
        ai_bar.progress(i / total)
        try:
            analysis = svc.analyze_privacy_policy(url, result)
            result["ai_analysis"] = analysis
            # Update DB record with AI analysis
            scan_cache.set(url, result)
            try:
                from database.operations import save_scan_result
                save_scan_result(url, result, analysis)
            except Exception as db_err:
                logger.warning(f"Could not update AI analysis for {url}: {db_err}")
        except Exception as e:
            logger.warning(f"AI analysis failed for {url}: {e}")
            result["ai_analysis"] = None

    ai_status.empty()
    ai_bar.empty()


def main():
    """Main function for batch scan page."""
    if "page" not in st.session_state:
        st.session_state.page = "batch_scan"
    
    render_batch_scan_page()


if __name__ == "__main__":
    main()
