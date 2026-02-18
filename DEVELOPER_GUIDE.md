# Developer Guide - Modular Application Architecture

## Quick Start

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### How Navigation Works
The application uses Streamlit's session state for page routing:

```python
# In sidebar (app.py)
if st.button("Quick Scan"):
    st.session_state.page = "quick_scan"
    st.rerun()  # Rerun to show new page

# Page rendering (app.py)
if st.session_state.page == "quick_scan":
    quick_scan_page()  # Shows quick_scan.py content
```

---

## Adding a New Page

### 1. Create New Page Module
Create `pages/my_new_page.py`:

```python
"""My New Page - Description"""

import streamlit as st
from components import render_header
from logger_config import get_logger

logger = get_logger(__name__)

def render_my_new_page():
    """Render the new page."""
    render_header()  # Consistent header
    
    st.markdown("# 📌 My New Page")
    st.markdown("*Page description*")
    
    # Your content here
    ...

def main():
    """Main function for new page."""
    if "page" not in st.session_state:
        st.session_state.page = "my_new_page"
    
    render_my_new_page()

if __name__ == "__main__":
    main()
```

### 2. Import in app.py
```python
from pages.my_new_page import render_my_new_page as my_new_page

# In main() function
elif st.session_state.page == "my_new_page":
    my_new_page()
```

### 3. Add Navigation Button
In the `render_sidebar()` function in app.py:

```python
pages = {
    # ... existing pages ...
    "my_new_page": ("📌 My New Page", "Description"),
}
```

---

## Adding a New Component

### 1. Create Component Module
Create `components/my_component.py`:

```python
"""My Component - Reusable UI element"""

import streamlit as st
from typing import Dict, Any

def render_my_component(data: Dict[str, Any]):
    """
    Render my custom component.
    
    Args:
        data: Component data dictionary
    """
    # Implementation here
    st.write(data)

def my_helper_function():
    """Helper function for component logic."""
    pass
```

### 2. Export from components/__init__.py
```python
from .my_component import render_my_component, my_helper_function

__all__ = [
    # ... existing exports ...
    "render_my_component",
    "my_helper_function",
]
```

### 3. Use in Pages
```python
from components import render_my_component

def render_my_page():
    render_my_component(data={"key": "value"})
```

---

## Adding a New Utility Library

### 1. Create Library Module
Create `libs/my_utility.py`:

```python
"""My Utility - Helper functions"""

import logging

logger = logging.getLogger(__name__)

class MyUtility:
    """Main utility class."""
    
    def process_data(self, input_data):
        """Process data."""
        logger.info(f"Processing data: {input_data}")
        return processed_data

def helper_function(param: str) -> str:
    """Helper function."""
    return result
```

### 2. Fix libs/__init__.py if needed
```python
"""Library modules for app utilities and helpers."""
```

### 3. Use in Code
```python
from libs.my_utility import MyUtility, helper_function

utility = MyUtility()
result = utility.process_data(input_data)
```

---

## Project Dependencies Map

```
app.py (router)
├─ pages/
│  ├─ dashboard.py → components + database.operations
│  ├─ quick_scan.py → components + controllers
│  ├─ batch_scan.py → components + controllers + libs.cache
│  ├─ history.py → components + database.operations
│  └─ settings.py → components + config
│
├─ components/ (UI building blocks)
│  └─ All import from validators, libs, etc.
│
└─ libs/ (utilities)
   ├─ cache.py
   ├─ export.py
   ├─ formatters.py
   ├─ progress.py
   └─ validators.py
```

---

## Best Practices

### 1. Component Design
- **Keep components small** - Focus on one responsibility
- **Pass data via props** - Don't access global state
- **Return clear values** - Document return types
- **Add docstrings** - Explain what each function does

```python
def good_component(data: Dict, on_change: callable = None):
    """
    Render component with data.
    
    Args:
        data: Input data dictionary
        on_change: Optional callback for changes
        
    Returns:
        None (renders to Streamlit)
    """
    # Implementation
```

### 2. Error Handling
Use custom exceptions from `exceptions.py`:

```python
from exceptions import ScanError, NetworkError

try:
    result = controller.scan_website(url)
except NetworkError as e:
    st.error(f"Network error: {e}")
    logger.error(f"Network error: {e}")
except ScanError as e:
    st.warning(f"Scan error: {e}")
```

### 3. Logging
Use the logger utility:

```python
from logger_config import get_logger

logger = get_logger(__name__)

logger.info("Starting scan")
logger.warning("Slow performance")
logger.error("Failed to scan", exc_info=True)
```

### 4. Caching
Use the cache for expensive operations:

```python
from libs.cache import ScanCache

cache = ScanCache(ttl_hours=24)

# Store result
cache.set("https://example.com", result)

# Retrieve if available
cached = cache.get("https://example.com")
if cached:
    return cached

# Otherwise compute and cache
result = expensive_operation()
cache.set("https://example.com", result)
```

### 5. Session State
Keep session state minimal and clear:

```python
# Good: Simple page tracking
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Good: Feature flags
if "show_advanced" not in st.session_state:
    st.session_state.show_advanced = False

# Avoid: Complex nested state
# st.session_state.user.profile.settings... (too complex)
```

---

## Testing Guide

### Unit Testing Components
```python
# tests/test_components.py
from components import render_scan_form

def test_scan_form_validation():
    is_valid, url, error = validate_and_prepare_url("invalid")
    assert not is_valid
    assert error is not None
```

### Integration Testing
```bash
# Run Streamlit in headless mode
streamlit run app.py --headless --logger.level=error

# Or with pytest-streamlit
pytest tests/ -v
```

### Manual Testing Checklist
- [ ] Navigation between all pages works
- [ ] Scan results display correctly
- [ ] Caching returns cached results
- [ ] Export functions work (CSV, JSON)
- [ ] Error handling shows user messages
- [ ] Database optional (works without it)
- [ ] API keys optional (works without them)

---

## Code Style

### Naming Conventions
```python
# Functions: snake_case
def render_component(): pass
def validate_input(): pass

# Classes: PascalCase
class ScanCache: pass
class ProgressTracker: pass

# Constants: UPPER_CASE
CACHE_TTL_HOURS = 24
BATCH_LIMIT = 100

# Private: _leading_underscore
def _private_helper(): pass
```

### Type Hints
Always include type hints:

```python
from typing import Dict, List, Optional, Tuple

def process_data(url: str, options: Dict[str, Any]) -> Tuple[bool, str]:
    """Process data and return result."""
    pass

def get_cached(key: str) -> Optional[Dict]:
    """Get from cache or None."""
    pass
```

### Docstring Format
```python
def my_function(param1: str, param2: int = 5) -> Dict[str, Any]:
    """
    Brief description of what function does.
    
    Longer description if needed, explaining the logic
    and why it's implemented this way.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 5)
        
    Returns:
        Dictionary with keys:
        - 'success': Boolean indicating success
        - 'data': The result data
        
    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not int
        
    Example:
        >>> result = my_function("test")
        >>> print(result['success'])
        True
    """
    pass
```

---

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = get_logger(__name__)
logger.debug("Debug message")
```

### Use st.write() for inspection
```python
import streamlit as st

st.write("Current page:", st.session_state.page)
st.write("Cache stats:", cache.get_stats())
st.write(data)  # Show any data structure
```

### Check Logs
```bash
# Logs are in logs/ directory
tail -f logs/compliance_checker.log
```

### Rerun debug
```python
# Check why page is rerunning
st.write("Rerun count:", st.session_state.get("rerun_count", 0))
```

---

## Performance Tips

1. **Cache expensive operations**
   ```python
   cache.set(key, result)
   ```

2. **Use st.session_state for state**
   ```python
   if st.session_state.key not in cache:
       # expensive operation
   ```

3. **Lazy load data**
   ```python
   if st.button("Load details"):
       # load only when requested
   ```

4. **Batch database queries**
   ```python
   # Bad: 100 queries
   for url in urls:
       db.query(Scan).filter_by(url=url).first()
   
   # Good: 1 query
   db.query(Scan).filter(Scan.url.in_(urls)).all()
   ```

---

## Common Issues & Solutions

### Issue: Import Error
**Solution:** Make sure __init__.py files exist and export functions

### Issue: Page Not Updating  
**Solution:** Call st.rerun() after changing session state

### Issue: Cache Not Working
**Solution:** Check TTL hasn't expired or clear with cache.clear_all()

### Issue: Slow Performance
**Solution:** Profile with st.write(time.time()), use caching, batch queries

---

## File Structure Quick Reference

```
project/
├── app.py                    # Main router (entry point)
├── config.py                 # Configuration management
├── constants.py              # Application constants
├── exceptions.py             # Custom exception classes
├── validators.py             # Input validation
├── logger_config.py          # Logging setup
│
├── pages/                    # Page-specific logic
│   ├── __init__.py
│   ├── dashboard.py          # Home/stats page
│   ├── quick_scan.py         # Single URL scan
│   ├── batch_scan.py         # Bulk URL scan
│   ├── history.py            # View past scans
│   └── settings.py           # Configuration UI
│
├── components/               # Reusable UI components
│   ├── __init__.py          # Exports all components
│   ├── header.py            # Header + navigation
│   ├── scan_form.py         # Form inputs
│   ├── results_display.py    # Results rendering
│   ├── batch_progress.py     # Progress UI
│   ├── comparison_tool.py    # Comparison UI
│   └── export_panel.py       # Export options
│
├── libs/                     # Utility libraries
│   ├── __init__.py          # Module export
│   ├── cache.py             # Result caching
│   ├── export.py            # CSV/JSON export
│   ├── formatters.py        # Data formatting
│   ├── progress.py          # Progress tracking
│   └── validators.py        # Input validation
│
├── controllers/              # Business logic
│   ├── compliance_controller.py  # Main logic
│   └── __init__.py
│
├── database/                 # Data layer
│   ├── db.py                # Connection management
│   ├── models.py            # SQLAlchemy models
│   ├── operations.py        # CRUD operations
│   └── __init__.py
│
├── models/                   # Data models
│   ├── compliance_model.py
│   └── __init__.py
│
├── services/                 # External integrations
│   ├── openai_service.py    # OpenAI integration
│   └── __init__.py
│
├── tests/                    # Test suite
│   ├── test_validators.py
│   └── test_openai_service.py
│
├── logs/                     # Application logs (auto-created)
│
└── docs/                     # Documentation
    ├── LATEST_UPDATE.md      # This update summary
    ├── README.md             # User documentation
    └── CONTRIBUTING.md       # Developer guide
```

---

## Summary

The modular architecture provides:
- **95% fewer lines in main app** (90 vs 783)
- **Reusable components** for easy extension
- **Clear separation** of concerns
- **Easy testing** at each layer
- **Scalable structure** for growth

Happy coding! 🚀
