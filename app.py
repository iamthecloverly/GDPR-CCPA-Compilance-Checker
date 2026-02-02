import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="GDPR/CCPA Compliance Checker",
    page_icon="🔒",
    layout="wide"
)

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
    st.sidebar.warning(f"⚠️ Running without database")
    st.sidebar.caption(f"Error: {str(e)}")
    
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
    st.error(f"Import Error: {str(e)}")
    st.code(traceback.format_exc())
    st.stop()

# Initialize services
controller = ComplianceController()
openai_service = OpenAIService()

# App title
st.title("🔒 GDPR/CCPA Compliance Checker")
st.markdown("Scan websites for privacy compliance indicators and get AI-powered recommendations.")

# Sidebar
st.sidebar.header("Settings")
ai_enabled = st.sidebar.checkbox(
    "Enable AI Analysis",
    value=bool(os.getenv("OPENAI_API_KEY")),
    help="Requires OPENAI_API_KEY to be set"
)

if ai_enabled and not os.getenv("OPENAI_API_KEY"):
    st.sidebar.error("OPENAI_API_KEY not found in environment variables")
    ai_enabled = False

# Main tabs
tab1, tab2, tab3 = st.tabs(["Single Scan", "Scan History", "Batch Scan"])

# Tab 1: Single Scan
with tab1:
    st.header("Single URL Scan")
    
    url = st.text_input(
        "Enter URL to scan",
        placeholder="https://example.com",
        help="Enter a complete URL including https://"
    )
    
    if st.button("Scan URL", type="primary"):
        if not url:
            st.error("Please enter a URL")
        elif not url.startswith(("http://", "https://")):
            st.error("URL must start with http:// or https://")
        else:
            with st.spinner("Scanning website..."):
                try:
                    # Perform compliance scan
                    results = controller.scan_website(url)
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Compliance Score", f"{results['score']:.1f}/100")
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
                    
                    # Details
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
                    
                    # AI Analysis
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
                                st.error(f"AI analysis failed: {str(e)}")
                    
                    # Save to database
                    if DB_AVAILABLE:
                        try:
                            scan_id = save_scan_result(url, results, ai_analysis)
                            st.success(f"✅ Scan saved to database (ID: {scan_id})")
                        except Exception as e:
                            st.warning(f"Could not save to database: {str(e)}")
                    
                    # Export option
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
                        f"compliance_report_{url.replace('https://', '').replace('/', '_')}.csv",
                        "text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Scan failed: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())

# Tab 2: Scan History
with tab2:
    st.header("Scan History")
    
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
                                "Date": scan.scan_date.strftime("%Y-%m-%d %H:%M"),
                                "Score": scan.score,
                                "Grade": scan.grade,
                                "Status": scan.status,
                                "Cookie Consent": scan.cookie_consent,
                                "Privacy Policy": scan.privacy_policy
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
            st.error(f"Error loading history: {str(e)}")
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

# Tab 3: Batch Scan
with tab3:
    st.header("Batch Scan")
    st.write("Scan multiple URLs at once (max 10)")
    
    urls_input = st.text_area(
        "Enter URLs (one per line)",
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
        height=200
    )
    
    if st.button("Scan All URLs", type="primary"):
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        
        if not urls:
            st.error("Please enter at least one URL")
        elif len(urls) > 10:
            st.error("Maximum 10 URLs allowed")
        else:
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
                        save_scan_result(url, result)
                        
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
