# Contributing to GDPR/CCPA Compliance Checker

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional. We're committed to providing a welcoming environment for all contributors.

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- Virtual environment tool (venv or conda)
- GitHub account

### Local Development Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/GDPR-CCPA-Compilance-Checker.git
cd GDPR-CCPA-Compilance-Checker

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install development dependencies
pip install -r requirements.txt
pip install black flake8 mypy pytest pytest-cov  # Dev tools

# 5. Create a feature branch
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Code Style

We follow PEP 8 with these tools:

```bash
# Format code with Black
black .

# Check style with flake8
flake8 . --max-line-length=100

# Type check with mypy
mypy . --strict-optional
```

### 2. Code Structure

Follow the MVC pattern:
- **Models** (`models/`): Data access and scraping
- **Controllers** (`controllers/`): Business logic orchestration
- **Services** (`services/`): External integrations
- **Database** (`database/`): ORM and CRUD operations
- **UI** (`app.py`): Streamlit frontend

### 3. Type Hints

All functions must have type hints:

```python
def analyze_compliance(self, url: str) -> Dict[str, Any]:
    """Detailed docstring here."""
    pass
```

### 4. Docstrings

Use Google-style docstrings:

```python
def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate and normalize a URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, normalized_url or error_message)
        
    Raises:
        InvalidURLError: If URL is invalid
        
    Example:
        >>> is_valid, url = validate_url("example.com")
        >>> assert is_valid
    """
    pass
```

### 5. Error Handling

Use custom exceptions from `exceptions.py`:

```python
from exceptions import ScanError, NetworkError, InvalidURLError

try:
    result = scan_website(url)
except NetworkError as e:
    logger.error(f"Network error: {e}")
    # Handle gracefully
except ScanError as e:
    logger.error(f"Scan error: {e}")
    # Handle gracefully
```

### 6. Logging

Use the logging module consistently:

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing {url}")
logger.warning(f"Retry attempt {attempt}/3")
logger.error(f"Failed to fetch: {e}")
logger.debug(f"Response status: {response.status_code}")
```

## Making Changes

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

### 2. Make Changes
- Keep commits atomic and focused
- Write clear commit messages
- Update docstrings and type hints
- Add logging statements for debugging

### 3. Test Your Changes

```bash
# Run the app locally
streamlit run app.py

# For batch operations, test with multiple URLs
# For database operations, ensure DB is available
# For AI features, set OPENAI_API_KEY environment variable
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add new compliance check for GDPR section 5"
git push origin feature/your-feature-name
```

Use conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (not UI)
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `test:` Adding tests
- `chore:` Maintenance

### 5. Submit Pull Request

1. Go to GitHub and create a Pull Request
2. Write a clear PR description:
   - What problem does it solve?
   - How does it solve it?
   - Are there any breaking changes?
   - Screenshots for UI changes

3. PR Template:
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How to Test
Steps to verify the changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings updated
- [ ] Logging added appropriately
- [ ] No new warnings
- [ ] Tested locally
```

## Key Areas for Contribution

### High Priority
1. **Async Scanning** - Convert batch scanning to async/concurrent
2. **Caching Layer** - Add Redis or in-memory cache for repeated scans
3. **Test Suite** - Comprehensive pytest coverage
4. **CI/CD Pipeline** - GitHub Actions workflow

### Medium Priority
1. **Database Migrations** - Alembic setup for schema versioning
2. **API Endpoint** - REST API wrapper for programmatic access
3. **Browser Extension** - Quick scan from any webpage
4. **Rate Limiting** - Prevent abuse and resource exhaustion

### Documentation
1. Architecture diagrams
2. API documentation
3. Deployment guides (Docker, Kubernetes)
4. Troubleshooting guide

## Testing Guidelines

When adding features, consider:
- Happy path (normal operation)
- Error cases (network failure, invalid input)
- Edge cases (empty response, timeout)
- Boundary conditions (max URLs, max size)

Example test structure:
```python
import pytest
from validators import validate_url, InvalidURLError

def test_validate_url_with_protocol():
    is_valid, url = validate_url("https://example.com")
    assert is_valid
    assert url == "https://example.com"

def test_validate_url_without_protocol():
    is_valid, url = validate_url("example.com")
    assert is_valid
    assert url == "https://example.com"

def test_validate_url_invalid():
    with pytest.raises(InvalidURLError):
        validate_url("not a url")
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for all public functions
- Include examples in docstrings
- Document breaking changes prominently

## Performance Considerations

- Use connection pooling for HTTP requests
- Cache frequently accessed data
- Batch database operations
- Monitor response times
- Profile with large datasets (100+ URLs)

## Security Checklist

- [ ] No API keys in code (use environment variables)
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (use ORM)
- [ ] HTTPS enforced for external requests
- [ ] Timeouts on network calls
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't log sensitive data

## Common Issues & Solutions

### Issue: Import errors after changes
**Solution:** Verify all imports are correct and run:
```bash
python -c "from models.compliance_model import ComplianceModel"
```

### Issue: Type checking fails
**Solution:** Ensure all function signatures have type hints:
```bash
mypy --strict-optional .
```

### Issue: App won't start
**Solution:** Check environment variables and database connectivity:
```bash
cp .env.example .env
# Edit .env with your settings
streamlit run app.py
```

### Issue: Network timeout errors
**Solution:** Increase REQUEST_TIMEOUT in config.py or .env

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Found a bug?** Open an Issue with reproduction steps
- **Feature request?** Open an Issue with use case
- **Security concern?** Email privately (don't open public issue)

## Review Process

1. Maintainers review PRs within 3-5 business days
2. May request changes or clarifications
3. Once approved, PR is merged to main
4. Changes deployed to Streamlit Cloud automatically

## Recognition

Contributors will be:
- Listed in README.md acknowledgments
- Credited in commit history
- Mentioned in release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to make privacy compliance accessible to everyone!** 🙏
