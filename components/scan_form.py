"""Scan form components."""

import streamlit as st
from typing import Tuple
from validators import validate_url
from exceptions import InvalidURLError, ValidationError


def render_scan_form() -> Tuple[str, bool]:
    """
    Render scan form with URL input and submit button.

    Returns:
        Tuple of (url: str, submitted: bool)
    """
    with st.form("scan_form", clear_on_submit=False):
        col1, col2 = st.columns([5, 1])

        with col1:
            url = st.text_input(
                label="Website URL",
                placeholder="https://example.com",
                help="Enter the complete URL including https://",
            )

        with col2:
            submitted = st.form_submit_button(
                "Scan →",
                use_container_width=True,
                type="primary",
            )

    st.markdown("""
<div class="scan-feature-row">
  <span class="scan-feature-pill">🍪 Cookie Consent</span>
  <span class="scan-feature-pill">📄 Privacy Policy</span>
  <span class="scan-feature-pill">🔍 Tracker Detection</span>
  <span class="scan-feature-pill">📬 Contact Info</span>
</div>
""", unsafe_allow_html=True)

    return url, submitted


def render_batch_upload_form() -> Tuple[str, bool]:
    """
    Render form for batch URL upload.

    Returns:
        Tuple of (csv_content: str, submitted: bool)
    """
    _MAX_CSV_BYTES = 5 * 1024 * 1024  # 5 MB

    tab1, tab2 = st.tabs(["📋  Paste URLs", "📎  Upload CSV"])

    csv_content_tab1 = ""
    csv_content_tab2 = ""
    submitted_tab1 = False
    submitted_tab2 = False

    with tab1:
        csv_content_tab1 = st.text_area(
            "URLs — one per line, or comma-separated",
            placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
            height=180,
        )
        col_btn, col_hint = st.columns([1, 3])
        with col_btn:
            submitted_tab1 = st.button(
                "Start Batch Scan →", key="batch_paste", type="primary", use_container_width=True
            )
        with col_hint:
            st.caption("Accepts plain domains (example.com) or full URLs — duplicates are removed automatically.")

    with tab2:
        uploaded_file = st.file_uploader(
            "Choose a CSV file (max 5 MB)",
            type=["csv"],
            help="Your CSV should have a column named 'url' — or just one column of URLs with no header.",
        )

        if uploaded_file:
            if uploaded_file.size > _MAX_CSV_BYTES:
                st.error("File too large. Maximum allowed size is 5 MB.")
            else:
                csv_content_tab2 = uploaded_file.getvalue().decode("utf-8")
                st.success(f"Loaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

        col_btn2, col_hint2 = st.columns([1, 3])
        with col_btn2:
            submitted_tab2 = st.button(
                "Start Batch Scan →", key="batch_upload", type="primary", use_container_width=True
            )
        with col_hint2:
            st.caption("CSV must have a 'url' column, or be a single-column list of URLs.")

    st.markdown("""
<div class="batch-help-row">
  <div class="batch-help-item"><span class="batch-help-icon">⚡</span>Up to 50 URLs scanned in parallel</div>
  <div class="batch-help-item"><span class="batch-help-icon">💾</span>Results cached — re-scan is instant</div>
  <div class="batch-help-item"><span class="batch-help-icon">📊</span>Export as CSV, JSON, or PDF</div>
  <div class="batch-help-item"><span class="batch-help-icon">🤖</span>Optional AI analysis per site</div>
</div>
""", unsafe_allow_html=True)

    if submitted_tab1:
        return csv_content_tab1, True
    elif submitted_tab2:
        return csv_content_tab2, True
    else:
        return "", False


def validate_and_prepare_url(raw_url: str) -> Tuple[bool, str, str]:
    """
    Validate URL and return (is_valid, url, error_message).
    
    Args:
        raw_url: User input URL string
        
    Returns:
        Tuple of (is_valid, prepared_url, error_message)
    """
    if not raw_url or not raw_url.strip():
        return False, "", "Please enter a website URL"
    
    try:
        is_valid, url = validate_url(raw_url)
        if not is_valid:
            return False, "", f"Invalid URL format: {raw_url}"
        return True, url, ""
    except InvalidURLError as e:
        return False, "", f"URL validation failed: {str(e)}"
    except ValidationError as e:
        return False, "", f"Validation error: {str(e)}"
    except Exception as e:
        return False, "", f"Error processing URL: {str(e)}"


def show_validation_error(message: str):
    """Display validation error in Streamlit."""
    st.error(message)


def validate_and_prepare_batch_urls(csv_content: str) -> Tuple[bool, list, str]:
    """
    Validate batch URLs from CSV/text content.
    
    Args:
        csv_content: Raw CSV or newline-separated URLs
        
    Returns:
        Tuple of (is_valid, urls_list, error_message)
    """
    if not csv_content or not csv_content.strip():
        return False, [], "Please enter or upload URLs"
    
    urls = []
    errors = []
    
    # Parse URLs
    lines = csv_content.strip().split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        # Handle comma-separated values
        for part in line.split(','):
            url = part.strip()
            if url:
                try:
                    is_valid, prepared_url = validate_url(url)
                    if is_valid:
                        urls.append(prepared_url)
                    else:
                        errors.append(f"Line {i}: Invalid URL '{url}'")
                except Exception as e:
                    errors.append(f"Line {i}: {str(e)}")
    
    if not urls:
        error_msg = "No valid URLs found"
        if errors:
            error_msg += "\n" + "\n".join(errors[:5])
        return False, [], error_msg

    # Deduplicate while preserving order
    seen: set = set()
    unique_urls = []
    duplicates = 0
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
        else:
            duplicates += 1
    urls = unique_urls

    if errors:
        st.warning(f"Skipped {len(errors)} invalid URL(s)\n" + "\n".join(errors[:3]))
    if duplicates:
        st.info(f"Removed {duplicates} duplicate URL(s).")

    return True, urls, ""
