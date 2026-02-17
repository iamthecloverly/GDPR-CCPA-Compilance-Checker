# CODE IMPROVEMENTS & OPTIMIZATION GUIDE

## 🎯 IMMEDIATE IMPROVEMENTS (Critical)

### 1. Add Input Validation & Sanitization
**Current Issue**: Limited front-end validation
**Solution**:
```python
# validators.py - Add these functions
def validate_csv_content(csv_content: str) -> Tuple[bool, List[str], str]:
    """Validate CSV for batch scanning"""
    import csv
    from io import StringIO
    
    try:
        urls = []
        reader = csv.DictReader(StringIO(csv_content))
        for row in reader:
            if 'url' not in row:
                return False, [], "CSV must have 'url' column"
            url = row['url'].strip()
            if url:
                urls.append(url)
        return True, urls, ""
    except Exception as e:
        return False, [], f"CSV parsing error: {str(e)}"

def sanitize_domain(domain: str) -> str:
    """Clean and normalize domain input"""
    domain = domain.strip().lower()
    # Remove common prefixes
    domain = domain.replace('www.', '')
    domain = domain.replace('http://', '')
    domain = domain.replace('https://', '')
    return domain
```

### 2. Implement Better Error Messages
**Current Issue**: Generic error messages
**Solution**:
```python
# Create new file: errors.py
class UserFriendlyError(Exception):
    """Base class for user-facing errors"""
    def __init__(self, user_message: str, technical_message: str = None):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        super().__init__(self.technical_message)

class URLError(UserFriendlyError):
    pass

class ScanTimeoutError(UserFriendlyError):
    pass

class RateLimitError(UserFriendlyError):
    pass

# Usage in app.py
try:
    results = controller.scan_website(url)
except RateLimitError as e:
    st.warning(f"⏳ {e.user_message}\n\nTip: Wait a moment and try again")
```

### 3. Add Progress Tracking for Long Operations
**Current Issue**: No feedback during long scans
**Solution**:
```python
# Create new file: progress_tracker.py
import time
from dataclasses import dataclass
from typing import Callable

@dataclass
class ProgressTracker:
    total_items: int
    start_time: float = None
    current_item: int = 0
    current_stage: str = ""
    
    def __post_init__(self):
        self.start_time = time.time()
    
    def update(self, current: int, stage: str = ""):
        self.current_item = current
        self.current_stage = stage
        
    def get_progress(self) -> dict:
        elapsed = time.time() - self.start_time
        rate = self.current_item / elapsed if elapsed > 0 else 0
        remaining = (self.total_items - self.current_item) / rate if rate > 0 else 0
        
        return {
            "current": self.current_item,
            "total": self.total_items,
            "percentage": (self.current_item / self.total_items * 100),
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": remaining,
            "stage": self.current_stage
        }

# Usage in app.py
tracker = ProgressTracker(total_items=50)
progress_bar = st.progress(0)
status_text = st.empty()

for url in urls:
    tracker.update(urls.index(url) + 1, f"Scanning {url}")
    results = scan_url(url)
    
    progress = tracker.get_progress()
    progress_bar.progress(progress["percentage"] / 100)
    status_text.write(f"Progress: {progress['current']}/{progress['total']} | "
                     f"Elapsed: {progress['elapsed_seconds']:.0f}s | "
                     f"Remaining: ~{progress['estimated_remaining_seconds']:.0f}s")
```

### 4. Implement Caching Strategy
**Current Issue**: No caching for frequent scans
**Solution**:
```python
# Create new file: cache.py
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class ScanCache:
    def __init__(self, ttl_hours: int = 24):
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Dict[str, Any]]:
        key = self._get_key(url)
        if key in self.cache:
            cached_data = self.cache[key]
            if datetime.now() - cached_data["timestamp"] < self.ttl:
                return cached_data["results"]
        return None
    
    def set(self, url: str, results: Dict[str, Any]) -> None:
        key = self._get_key(url)
        self.cache[key] = {
            "results": results,
            "timestamp": datetime.now()
        }
    
    def clear_expired(self) -> None:
        now = datetime.now()
        expired_keys = [k for k, v in self.cache.items() 
                       if now - v["timestamp"] > self.ttl]
        for key in expired_keys:
            del self.cache[key]

# Usage in controllers/compliance_controller.py
cache = ScanCache(ttl_hours=24)

def scan_website(self, url: str):
    # Check cache first
    cached = cache.get(url)
    if cached:
        logger.info(f"Returning cached results for {url}")
        return cached
    
    # Perform scan
    results = # ... scan logic ...
    cache.set(url, results)
    return results
```

### 5. Add Comprehensive Logging
**Current Issue**: Limited debug information
**Solution**:
```python
# Enhance logger_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging(level=logging.INFO):
    """Setup comprehensive logging with JSON output"""
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # File handler with JSON format
    file_handler = logging.FileHandler('logs/app.json')
    json_formatter = jsonlogger.JsonFormatter()
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with readable format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Usage - structured logging
logger.info("Scan initiated", extra={
    "url": url,
    "user_id": user_id,
    "timestamp": datetime.now().isoformat()
})
```

---

## 🚀 PERFORMANCE OPTIMIZATIONS

### 1. Database Query Optimization
**Current Issue**: N+1 queries in loops
**Solution**:
```python
# database/operations.py - Add batch operations
from sqlalchemy import and_

def get_scans_by_urls(urls: List[str]) -> Dict[str, List[Dict]]:
    """Get all scans for multiple URLs in single query"""
    with get_db() as db:
        if db is None:
            return {}
        
        scans = db.query(ComplianceScan).filter(
            ComplianceScan.url.in_(urls)
        ).all()
        
        result = {url: [] for url in urls}
        for scan in scans:
            result[scan.url].append({
                'score': scan.score,
                'grade': scan.grade,
                'scan_date': scan.scan_date
            })
        return result
```

### 2. Implement Request Batching
**Current Issue**: Individual HTTP requests for each domain check
**Solution**:
```python
# models/compliance_model.py - Add concurrent requests
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncComplianceModel(ComplianceModel):
    async def analyze_compliance_async(self, url: str):
        """Async version for concurrent processing"""
        # Implementation using aiohttp
        pass
    
    async def batch_analyze(self, urls: List[str]):
        """Analyze multiple URLs concurrently"""
        tasks = [self.analyze_compliance_async(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Add Response Streaming for Large Reports
**Current Issue**: Large exports may timeout
**Solution**:
```python
# Add to app.py for CSV export
def stream_csv_export(scans: List[Dict]):
    """Stream CSV export to avoid memory issues"""
    import io
    import csv
    
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=['url', 'score', 'grade', 'date'])
    writer.writeheader()
    
    for scan in scans:
        writer.writerow(scan)
        yield buffer.getvalue()
        buffer.truncate(0)
        buffer.seek(0)
```

---

## 🔒 SECURITY ENHANCEMENTS

### 1. Add Rate Limiting
```python
# Create new file: security.py
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        return False
```

### 2. Input Sanitization
```python
# validators.py - Add sanitization
def sanitize_for_display(text: str, max_length: int = 500) -> str:
    """Sanitize user input for display"""
    import html
    text = html.escape(text)
    return text[:max_length] + "..." if len(text) > max_length else text
```

---

## ♿ ACCESSIBILITY IMPROVEMENTS

### 1. Add ARIA Labels
```python
# components/accessible_components.py
def accessible_button(label: str, callback=None, **kwargs):
    """Create button with accessibility features"""
    html = f'<button aria-label="{label}" role="button">'
    html += label
    html += '</button>'
    return st.button(label, **kwargs)  # Use Streamlit's built-in accessibility
```

### 2. Add Keyboard Navigation
```python
st.write("""
<script>
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'k') {
        event.preventDefault();
        document.querySelector('[data-testid="textInput"]').focus();
    }
});
</script>
""", unsafe_allow_html=True)
```

---

## 📊 MONITORING & OBSERVABILITY

### 1. Add Metrics Collection
```python
# Create new file: metrics.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ScanMetrics:
    total_scans: int = 0
    successful_scans: int = 0
    failed_scans: int = 0
    average_scan_time: float = 0
    average_score: float = 0
    
    def get_success_rate(self) -> float:
        if self.total_scans == 0:
            return 0
        return (self.successful_scans / self.total_scans) * 100

# Usage in controllers
metrics = ScanMetrics()
metrics.total_scans += 1
metrics.successful_scans += 1 if success else 0
```

### 2. Add Health Check Endpoint
```python
# Add to app.py - hidden debug page
def show_health_check():
    st.write("""
    ### System Health Check
    """)
    
    checks = {
        "Database": {"status": "✓" if DB_AVAILABLE else "✗"},
        "API Key": {"status": "✓" if os.getenv("OPENAI_API_KEY") else "✗"},
        "Network": {"status": "✓"},  # Add network test
    }
    
    st.json(checks)
```

---

## 📦 REFACTORING ROADMAP

### Phase 1: Extract Components
```
components/
├── __init__.py
├── header.py          # Header with logo and search
├── metrics_cards.py   # Stat cards/badges
├── score_display.py   # Large score visualization
├── scan_form.py       # Input form with validation
├── results_table.py   # Reusable table component
├── charts.py          # Plotly chart wrappers
└── modals.py          # Modal/dialog components
```

### Phase 2: Create Pages Structure
```
pages/
├── dashboard.py       # Main landing page
├── quick_scan.py      # Single URL scanning
├── batch_scan.py      # Bulk scanning
├── history.py         # View past scans
├── settings.py        # Configuration
└── help.py            # Documentation
```

### Phase 3: Add Utilities
```
utils/
├── formatters.py      # Date, score, size formatting
├── validators.py      # Input validation helpers
├── cache.py          # Caching utilities
├── metrics.py        # Metrics tracking
└── export.py         # CSV/PDF export
```

---

## 🧪 TESTING RECOMMENDATIONS

### 1. Unit Tests
```python
# tests/test_validators.py
def test_validate_csv_content():
    valid_csv = "url\nhttps://example.com"
    valid, urls, msg = validate_csv_content(valid_csv)
    assert valid == True
    assert len(urls) == 1
```

### 2. Integration Tests
```python
# tests/test_scan_workflow.py
def test_full_scan_workflow():
    # Test: Input -> Validation -> Scan -> Results
    pass
```

### 3. Performance Tests
```python
# tests/test_performance.py
def test_batch_scan_performance():
    # Ensure batch scan completes in reasonable time
    pass
```

---

## 📋 CHECKLIST FOR IMMEDIATE IMPLEMENTATION

- [ ] Add input validation functions
- [ ] Create better error messages
- [ ] Implement progress tracking
- [ ] Add caching layer
- [ ] Improve logging
- [ ] Extract reusable components
- [ ] Add rate limiting
- [ ] Create health check endpointexclude [ ] Add unit tests
- [ ] Optimize database queries
- [ ] Add documentation

