import streamlit as st
import os
import traceback
import logging
from datetime import datetime
from urllib.parse import urlparse
import pandas as pd

# Page config
st.set_page_config(
    page_title="GDPR/CCPA Compliance Checker",
    page_icon="🔒",
    layout="wide"
)

# Modern dark theme styling
st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }
    .stApp {
        background: radial-gradient(1200px 800px at 10% -10%, #1a2a3a 0%, #0b0f14 35%, #0b0f14 100%);
        color: #e6edf3;
    }
    section[data-testid="stSidebar"] {
        background: rgba(8, 12, 18, 0.95);
        border-right: 1px solid rgba(148, 163, 184, 0.12);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        color: #e6edf3;
    }
    header[data-testid="stHeader"] {
        background: rgba(8, 12, 18, 0.85);
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    h1, h2, h3, h4, h5 {
        color: #e6edf3;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        background: linear-gradient(135deg, rgba(22, 35, 51, 0.9), rgba(12, 18, 26, 0.9));
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 18px;
        padding: 28px 32px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-bottom: 0.75rem;
    }
    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #7dd3fc;
        margin-right: 8px;
        margin-top: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #cbd5e1;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 8px 14px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.12);
        border-color: rgba(56, 189, 248, 0.5);
        color: #e6edf3;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        color: white;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.25);
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background: rgba(15, 23, 42, 0.85) !important;
        color: #e6edf3 !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 10px !important;
    }
    .stMetric {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 12px 16px;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
DEBUG = os.getenv("APP_DEBUG", "").lower() in {"1", "true", "yes"}

# Helpers
def normalize_url(raw_url: str, assume_https: bool = True) -> str:
    if not raw_url:
        return ""
    url = raw_url.strip()
    if assume_https and not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False

def safe_filename_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        base = parsed.netloc or "report"
        return base.replace(":", "_")
    except Exception:
        return "report"

# Initialize database
DB_AVAILABLE = False
try:
    from database.db import init_db
    if os.getenv("DATABASE_URL"):
        init_db()
        DB_AVAILABLE = True
        st.sidebar.success("✅ Database connected")
except Exception as e:
    DB_AVAILABLE = False
    st.sidebar.warning("⚠️ Running without database")
    if DEBUG:
        st.sidebar.caption(f"Error: {str(e)}")
    logger.exception("Database initialization failed")
    
# Import operations after database initialization
try:
    from database.operations import (
        save_scan_result, 
        get_scan_history, 
        get_score_trend, 
        get_all_scanned_urls
    )
    from controllers.compliance_controller import ComplianceController
    from services.openai_service import OpenAIService
except ImportError as e:
    st.error("The app failed to start due to a missing dependency.")
    if DEBUG:
        st.code(traceback.format_exc())
    logger.exception("Import error during startup")
    st.stop()

# Initialize services
controller = ComplianceController()
openai_service = OpenAIService()

# App title
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🔒 GDPR/CCPA Compliance Checker</div>
        <div class="hero-subtitle">Modern privacy compliance scanning with AI-powered insights and export-ready reports.</div>
        <span class="pill">Fast scans</span>
        <span class="pill">AI analysis</span>
        <span class="pill">Audit-ready exports</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.header("Settings")
assume_https = st.sidebar.checkbox(
    "Assume https:// if missing",
    value=True,
    help="Automatically add https:// when you paste a bare domain"
)
ai_enabled = st.sidebar.checkbox(
    "Enable AI Analysis",
    value=bool(os.getenv("OPENAI_API_KEY")),
    help="Requires OPENAI_API_KEY to be set"
)

if ai_enabled and not os.getenv("OPENAI_API_KEY"):
    st.sidebar.error("OPENAI_API_KEY not found in environment variables")
    ai_enabled = False

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Use full URLs to improve scan accuracy.")
with st.sidebar.expander("How it works"):
    st.write("1) Enter a URL\n2) Run a scan\n3) Review score and details\n4) Export CSV")

# Main tabs
tab1, tab2, tab3 = st.tabs(["Single Scan", "Scan History", "Batch Scan"])

# Tab 1: Single Scan
with tab1:
    st.header("Single URL Scan")
    st.caption("Enter a website URL to check for privacy compliance signals.")
    
    with st.form("single_scan_form"):
        raw_url = st.text_input(
            "Enter URL to scan",
            placeholder="https://example.com",
            help="Enter a complete URL including https://"
        )
        submitted = st.form_submit_button("Scan URL", type="primary")

    if submitted:
        url = normalize_url(raw_url, assume_https=assume_https)
        if not url:
            st.error("Please enter a URL")
        elif not is_valid_url(url):
            st.error("Please enter a valid URL (http:// or https://)")
        else:
            with st.spinner("Scanning website..."):
                try:
                    results = controller.scan_website(url)
                    st.session_state["last_results"] = {
                        "url": url,
                        "results": results
                    }
                except Exception as e:
                    logger.exception("Scan failed")
                    st.error("Scan failed. Please try again or check the URL.")
                    st.info("Tip: Some sites block automated requests. Try again later.")
                    if DEBUG:
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

    if st.session_state.get("last_results"):
        url = st.session_state["last_results"]["url"]
        results = st.session_state["last_results"]["results"]

        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Compliance Score", f"{results['score']:.1f}/100")
            st.progress(max(0.0, min(1.0, results["score"] / 100)))
        with col2:
            grade_color = {
                "A": "🟢", "B": "🟡", "C": "🟠",
                "D": "🔴", "F": "⛔"
            }
            st.metric("Grade", f"{grade_color.get(results['grade'], '❓')} {results['grade']}")
        with col3:
            status_emoji = {
                "Compliant": "✅",
                "Needs Improvement": "⚠️",
                "Non-Compliant": "❌"
            }
            st.metric("Status", f"{status_emoji.get(results['status'], '❓')} {results['status']}")

        st.subheader("Compliance Details")
        details_col1, details_col2 = st.columns(2)

        with details_col1:
            st.write("**Cookie Consent:**", results["cookie_consent"])
            st.write("**Privacy Policy:**", results["privacy_policy"])

        with details_col2:
            st.write("**Contact Info:**", results["contact_info"])
            st.write("**Trackers Found:**", len(results.get("trackers", [])))

        if results.get("trackers"):
            with st.expander("View Detected Trackers"):
                for tracker in results["trackers"]:
                    st.code(tracker)

        ai_analysis = None
        if ai_enabled:
            st.subheader("AI-Powered Analysis")
            with st.spinner("Analyzing privacy policy..."):
                try:
                    ai_analysis = openai_service.analyze_privacy_policy(
                        url,
                        results
                    )
                    if ai_analysis:
                        st.markdown(ai_analysis)
                    else:
                        st.warning("AI analysis unavailable")
                except Exception as e:
                    logger.exception("AI analysis failed")
                    st.error("AI analysis failed. Please try again later.")
                    if DEBUG:
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

        if DB_AVAILABLE:
            try:
                scan_id = save_scan_result(url, results, ai_analysis)
                st.success(f"✅ Scan saved to database (ID: {scan_id})")
            except Exception as e:
                logger.exception("Could not save scan")
                st.warning("Could not save to database")
                if DEBUG:
                    st.caption(str(e))

        st.subheader("Export Results")
        export_data = {
            "URL": [url],
            "Score": [results["score"]],
            "Grade": [results["grade"]],
            "Status": [results["status"]],
            "Cookie Consent": [results["cookie_consent"]],
            "Privacy Policy": [results["privacy_policy"]],
            "Contact Info": [results["contact_info"]],
            "Trackers": [len(results.get("trackers", []))],
            "Scan Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Report (CSV)",
            csv,
            f"compliance_report_{safe_filename_from_url(url)}.csv",
            "text/csv"
        )

# Tab 2: Scan History
with tab2:
    st.header("Scan History")
    st.caption("Review previous scans and visualize trends over time.")
    
    if not DB_AVAILABLE:
        st.info("Database not available. History tracking is disabled.")
    else:
        try:
            scanned_urls = get_all_scanned_urls()
            
            if not scanned_urls:
                st.info("No scan history available yet. Perform your first scan!")
            else:
                selected_url = st.selectbox("Select URL to view history", scanned_urls)
                
                if selected_url:
                    history = get_scan_history(selected_url, limit=20)
                    
                    if history:
                        st.subheader(f"History for {selected_url}")
                        
                        # Display history table
                        history_data = []
                        for scan in history:
                            history_data.append({
                                "Date": scan['scan_date'].strftime("%Y-%m-%d %H:%M"),
                                "Score": scan['score'],
                                "Grade": scan['grade'],
                                "Status": scan['status'],
                                "Cookie Consent": scan['cookie_consent'],
                                "Privacy Policy": scan['privacy_policy']
                            })
                        
                        df = pd.DataFrame(history_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Score trend chart
                        st.subheader("Compliance Score Trend")
                        trend_data = get_score_trend(selected_url)
                        
                        if trend_data:
                            trend_df = pd.DataFrame(trend_data, columns=["Date", "Score"])
                            st.line_chart(trend_df.set_index("Date"))
                    else:
                        st.info("No history available for this URL")
        except Exception as e:
            logger.exception("Error loading history")
            st.error("Error loading history. Please try again later.")
            if DEBUG:
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
                
# Tab 3: Batch Scan
with tab3:
    st.header("Batch Scan")
    st.write("Scan multiple URLs at once (max 10)")
    st.caption("Best for comparing multiple sites quickly.")
    
    urls_input = st.text_area(
        "Enter URLs (one per line)",
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
        height=200
    )
    
    if st.button("Scan All URLs", type="primary"):
        raw_urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        normalized_urls = [normalize_url(u, assume_https=assume_https) for u in raw_urls]
        urls = []
        invalid_urls = []

        for url in normalized_urls:
            if is_valid_url(url):
                urls.append(url)
            else:
                invalid_urls.append(url)

        # Deduplicate while preserving order
        urls = list(dict.fromkeys(urls))

        if not urls:
            st.error("Please enter at least one valid URL")
            if invalid_urls:
                with st.expander("Invalid URLs"):
                    st.write("\n".join(invalid_urls))
        elif len(urls) > 10:
            st.error("Maximum 10 URLs allowed")
        else:
            if invalid_urls:
                st.warning("Some URLs were invalid and will be skipped.")
                with st.expander("Invalid URLs"):
                    st.write("\n".join(invalid_urls))

            results_list = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, url in enumerate(urls):
                status_text.text(f"Scanning {i+1}/{len(urls)}: {url}")

                try:
                    result = controller.scan_website(url)
                    result["url"] = url
                    results_list.append(result)

                    if DB_AVAILABLE:
                        try:
                            save_scan_result(url, result)
                        except Exception:
                            logger.exception("Batch save failed")
                except Exception as e:
                    st.warning(f"Failed to scan {url}: {str(e)}")

                progress_bar.progress((i + 1) / len(urls))

            status_text.text("✅ Batch scan complete!")
            
            # Display results
            if results_list:
                st.subheader("Batch Scan Results")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_score = sum(r["score"] for r in results_list) / len(results_list)
                    st.metric("Average Score", f"{avg_score:.1f}/100")
                with col2:
                    compliant = sum(1 for r in results_list if r["status"] == "Compliant")
                    st.metric("Compliant Sites", f"{compliant}/{len(results_list)}")
                with col3:
                    avg_trackers = sum(len(r.get("trackers", [])) for r in results_list) / len(results_list)
                    st.metric("Avg Trackers", f"{avg_trackers:.1f}")
                
                # Results table
                batch_data = []
                for result in results_list:
                    batch_data.append({
                        "URL": result["url"],
                        "Score": result["score"],
                        "Grade": result["grade"],
                        "Status": result["status"],
                        "Cookie Consent": result["cookie_consent"],
                        "Privacy Policy": result["privacy_policy"],
                        "Trackers": len(result.get("trackers", []))
                    })
                
                df = pd.DataFrame(batch_data)
                st.dataframe(df, use_container_width=True)
                
                # Export
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Batch Results (CSV)",
                    csv,
                    f"batch_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

# Footer
st.markdown("---")
st.markdown(
    "**Note:** This tool provides automated compliance indicators. "
    "Consult legal professionals for comprehensive compliance review."
)
