# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit-based web application for GDPR/CCPA privacy compliance scanning. It performs web scraping to detect cookie consent banners, privacy policies, contact information, and third-party trackers, then generates compliance scores and AI-powered analysis using OpenAI GPT models.

## Common Commands

### Development

```bash
# Run the application
streamlit run app.py

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_validators.py

# Run a specific test class/method
python -m pytest tests/test_validators.py::TestValidators
python -m pytest tests/test_validators.py::TestValidators::test_validate_api_key_valid
```

### Code Quality

```bash
# Format code
black .

# Check style
flake8 . --max-line-length=120

# Sort imports
isort . --profile black

# Type checking
mypy . --ignore-missing-imports

# Run pre-commit hooks on all files
pre-commit run --all-files
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### Data Flow

1. **Entry Point** (`app.py`): Streamlit UI with custom CSS, sidebar navigation, and page routing
2. **Pages** (`app_pages/`): Dashboard, quick scan, batch scan, and history views
3. **Components** (`components/`): Reusable Streamlit UI widgets (scan form, results display, export panel, comparison tool, batch progress)
4. **Controller** (`controllers/compliance_controller.py`): Orchestrates scans, calculates scores/grades, manages caching
5. **Models** (`models/compliance_model.py`): Web scraping engine using BeautifulSoup4 with retry logic
6. **Services** (`services/openai_service.py`): AI-powered privacy policy analysis via OpenAI API
7. **Database** (`database/`): SQLAlchemy ORM with PostgreSQL/SQLite for scan history persistence
8. **Libs** (`libs/`): Utility libraries — `cache.py` (client-side `ScanCache`), `export.py`, `formatters.py`, `progress.py`, `validators.py` (domain/API key validation)

### Key Components

**Scoring Algorithm** (`constants.py`, `controllers/compliance_controller.py`):
- Cookie Consent: 30 points (banner detection via keywords/patterns)
- Privacy Policy: 30 points (link detection with regex patterns)
- Contact Info: 20 points (email/phone regex matching)
- Trackers: -20 points max (script src matching 18+ known tracking domains)
- Grades: A (90+), B (80-89), C (70-79), D (60-69), F (<60)

**Configuration** (`config.py`): Centralized env-based config with validation
- Database URL, OpenAI settings, scoring weights
- Timeouts, retry logic, batch limits
- Domain allowlist/blocklist support

**Custom Exceptions** (`exceptions.py`): Hierarchical error handling
- Base: `ComplianceCheckerError`
- Specific: `ScanError`, `NetworkError`, `AIServiceError`, `ValidationError`, etc.

**Security Features**:
- SSRF protection via URL validators (`validators.py`)
- Input sanitization (max 10,000 chars, protocol enforcement)
- Domain allowlist/blocklist support
- Prompt injection defenses in OpenAI system prompts
- CSV injection protection in export functions

### Caching

Two cache layers exist:
- **Server-side** (`controllers/compliance_controller.py`): `cachetools.TTLCache` with thread-safe locking, configured via `CACHE_TTL_SECONDS` and `CACHE_MAXSIZE` in `config.py`
- **Client-side** (`libs/cache.py`): `ScanCache` class with hour-based TTL and MD5-keyed storage, exposed via `get_scan_cache()` singleton

### Validators

Two validator modules with different responsibilities:
- `validators.py` (root): URL validation with SSRF protection — blocks private IPs, enforces protocols, applies domain allowlist/blocklist
- `libs/validators.py`: Domain format and API key validation without SSRF logic

### Testing Pattern

Tests are written with `unittest` (test classes extend `unittest.TestCase`) but executed via `pytest`. Test files in `tests/` directory:
- Name tests descriptively (e.g., `test_validate_url_with_protocol`)
- Use `self.subTest()` for parameterized assertions
- Mock external HTTP calls and OpenAI API

## Important Code Patterns

### Import Pattern
All modules use absolute imports with project root path setup in `app.py`:
```python
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### HTTP Requests
Always use `utils.create_session()` and `utils.safe_request()` for retry logic, timeouts, and security:
```python
from utils import create_session, safe_request
session = create_session()
response = safe_request(session, url, timeout=Config.REQUEST_TIMEOUT)
```

### Logging Pattern
```python
import logging
logger = logging.getLogger(__name__)
# Use logger.info(), logger.warning(), logger.exception() for operations
```

### Type Hints
All functions must have type hints. Use `Dict[str, Any]`, `List[Dict[str, Any]]` for complex return types.

### Docstrings
Use Google-style docstrings with Args, Returns, Raises, and Example sections.
