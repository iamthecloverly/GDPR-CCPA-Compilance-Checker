"""Scan form components."""

import streamlit as st
from typing import Tuple
from validators import validate_url
from exceptions import InvalidURLError, ValidationError


def render_scan_form() -> Tuple[str, bool]:
    """
    Render improved scan form with validation.
    
    Returns:
        Tuple of (url: str, submitted: bool)
    """
    st.subheader("Enter URL to Scan")
    st.caption("Paste the domain you want to analyze for compliance issues")
    
    with st.form("scan_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            url = st.text_input(
                label="Website URL",
                placeholder="https://example.com",
                help="Enter complete URL with protocol (http:// or https://)",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button(
                "Scan",
                width='stretch',
                type="primary"
            )
    
    return url, submitted


def render_batch_upload_form() -> Tuple[str, bool]:
    """
    Render form for batch URL upload.
    
    Returns:
        Tuple of (csv_content: str, submitted: bool)
    """
    st.subheader("Upload Multiple URLs")
    st.caption("Paste URLs separated by commas or newlines, or upload a CSV file")
    
    # Tab interface for different input methods
    tab1, tab2 = st.tabs(["Paste URLs", "Upload CSV"])
    
    with tab1:
        csv_content = st.text_area(
            "URLs (comma or newline separated)",
            placeholder="example1.com\nexample2.com\nexample3.com",
            height=150,
            label_visibility="collapsed"
        )
        submitted = st.button("Start Batch Scan", key="batch_paste")
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="CSV file should have a 'url' column"
        )
        
        if uploaded_file:
            csv_content = uploaded_file.getvalue().decode('utf-8')
        else:
            csv_content = ""
        
        submitted = st.button("Start Batch Scan", key="batch_upload")
    
    return csv_content, submitted


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
    
    if errors:
        st.warning(f"Skipped {len(errors)} invalid URLs\n" + "\n".join(errors[:3]))
    
    return True, urls, ""
