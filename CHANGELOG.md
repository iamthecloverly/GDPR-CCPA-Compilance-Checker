# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive type hints throughout codebase
- Custom exception hierarchy for proper error handling
- Input validation module with URL, batch, and API key validators
- Structured logging configuration with rotating file handlers
- Configuration management module (config.py)
- Constants module with keywords, domains, and patterns
- Detailed docstrings (Google style) for all modules and functions
- CONTRIBUTING.md guide for developers
- Extended README with architecture documentation
- Batch scan URL deduplication
- Debug mode toggle in sidebar
- Improved error messages with actionable tips
- Custom exception handling in main scan flow
- Database error handling with graceful fallbacks

### Changed
- Refactored ComplianceModel to use Config settings
- Updated ComplianceController to support weighted scoring
- Enhanced OpenAIService with better error handling
- Improved database operations with type hints and logging
- Updated app.py to use new validation layer
- Batch scan now validates all URLs before processing
- Exception handling improved with specific error types
- Logging statements added to all critical operations

### Fixed
- Input border styling for dark theme
- Metric text visibility with proper color overrides
- URL normalization for consistent processing
- Session management in database operations
- Error messages now provide actionable guidance
- Build artifacts properly gitignored

### Removed
- Hardcoded configuration values
- Generic exception handling (replaced with specific types)
- Inline magic numbers (moved to config)

### Security
- Environment variable validation
- Input sanitization for all user inputs
- API key format validation
- SQL injection prevention via ORM
- HTTPS enforcement for external requests
- Timeout enforcement on network calls

### Performance
- Connection pooling for HTTP requests
- Session reuse across multiple requests
- Database session detachment optimization
- Batch scanning with progress indicators

## [1.0.0] - 2025-02-02

### Added
- Initial release
- Single URL compliance scanning
- Batch scanning (up to 10 URLs)
- Compliance scoring (0-100) with grade assignment
- Cookie consent detection
- Privacy policy link detection
- Contact information detection
- Third-party tracker identification
- AI-powered privacy policy analysis via OpenAI GPT-4o-mini
- Scan history tracking with database persistence
- Score trend visualization
- CSV export for scan results
- Modern dark theme with glassmorphism effects
- Responsive Streamlit UI
- HTTP retry logic with exponential backoff
- HTML content validation
- Database support (SQLite/PostgreSQL)
- Environment variable configuration
- Debug mode for development

### Features
- Real-time scan progress indicators
- Compliance status determination (Compliant/Needs Improvement/Non-Compliant)
- Detailed findings breakdown
- AI remediation advice generation
- Scan history per URL
- Score trend analysis
- Batch URL validation
- Error handling with helpful tips

---

## Release Notes

### Version 1.0.0
**Initial Production Release** - Fully functional privacy compliance scanner with AI assistance.

Key capabilities:
- Automated compliance checking
- AI-powered analysis
- Database-backed history
- Production-ready UI
- Comprehensive error handling

**Known Limitations:**
- Max 10 URLs per batch
- OpenAI API required for AI features
- Database optional (works in-memory)
- Streamlit app vs REST API

### Version 1.1.0 (Planned)
- Async batch scanning for better performance
- Redis caching layer
- API endpoint for programmatic access
- Comprehensive test suite
- GitHub Actions CI/CD
- Docker containerization
- Browser extension

---

## How to Upgrade

### From development to next release:
```bash
git fetch origin
git checkout main
pip install -r requirements.txt
# Review .env for any new configuration options
```

### Breaking Changes
None in current version. All changes are backward compatible.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style
- Commit messages
- Pull request process
- Testing requirements
- Documentation standards

---

## Support

For issues or questions:
- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Email: [Contact maintainers]

---

**Last Updated:** February 2, 2025
