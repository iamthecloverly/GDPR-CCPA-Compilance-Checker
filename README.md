# GDPR/CCPA Compliance Checker

A modern, AI-assisted privacy compliance scanner for quick GDPR/CCPA signals and audit-ready exports.

---

## 🚀 [**Try Live Demo →**](https://gdpr-ccpa-compilance-checker.streamlit.app/)

---

## Why it matters

This project turns privacy compliance checks into a fast, repeatable workflow. It automates discovery of cookie consent banners, privacy policy links, contact info, and third‑party trackers, then summarizes risk with a clear score, grade, and recommendations. The result is a lightweight tool that helps teams prioritize privacy fixes and create shareable reports in minutes.

## What I built

- Single and batch scanning with clear scoring and exportable CSV reports.
- AI‑assisted policy review that highlights strengths, gaps, and remediation steps.
- Historical tracking with score trends (database‑backed) for ongoing monitoring.

## What I learned

- Building reliable web scraping with retries, timeouts, and HTML validation.
- Designing a production‑ready Streamlit UI with glassmorphism and performance‑friendly styling.
- Structuring a clean MVC‑style Python app and integrating external AI services safely.

---

## 📋 Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│         Modern dark theme, responsive layouts           │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌─────────────┐
   │ Models │ │Services│ │ Controllers │
   └────────┘ └────────┘ └─────────────┘
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
           ┌──────────────────┐
           │   Config Layer   │
           │ (env, constants, │
           │   validation)    │
           └──────────────────┘
                   │
                   ▼
           ┌──────────────────┐
           │    Database      │
           │   (SQLAlchemy)   │
           └──────────────────┘
```

### Component Overview

#### **Models** (`models/compliance_model.py`)
- **ComplianceModel**: Web scraping engine with retry logic
  - Detects cookie consent banners
  - Identifies privacy policy links
  - Extracts contact information (email, phone)
  - Identifies third-party trackers
  - Features: HTTP retry, connection pooling, timeout handling

#### **Controllers** (`controllers/compliance_controller.py`)
- **ComplianceController**: Orchestration layer
  - `scan_website()`: Single URL scan with full analysis
  - `_calculate_score()`: Weighted scoring algorithm
  - `_calculate_grade()`: Letter grade assignment (A-F)
  - `_determine_status()`: Compliance status determination
  - `batch_scan()`: Multi-URL scanning with error handling

#### **Services** (`services/openai_service.py`)
- **OpenAIService**: AI-powered analysis
  - `analyze_privacy_policy()`: GPT-powered compliance assessment
  - `get_remediation_advice()`: Actionable fix recommendations
  - `_fetch_privacy_policy()`: Privacy policy retrieval
  - Graceful degradation when API key unavailable

#### **Database** (`database/`)
- **models.py**: ComplianceScan ORM model
  - Stores: URL, score, grade, findings, scan date, AI analysis
- **operations.py**: CRUD operations with logging
  - `save_scan_result()`: Persist scan data
  - `get_scan_history()`: Retrieve historical scans
  - `get_score_trend()`: Track compliance improvements
  - `get_all_scanned_urls()`: URL inventory
  - `get_latest_scan()`: Most recent scan for URL
- **db.py**: SQLAlchemy engine with SSL support

#### **Configuration** (`config.py`)
- Centralized environment management
- Database URL, OpenAI settings, scoring weights, timeouts, batch limits
- Features: Debug mode, max retries, backoff factors

#### **Validators** (`validators.py`)
- Input validation and sanitization
  - `validate_url()`: URL format and protocol checking
  - `validate_batch_urls()`: Batch validation with detailed errors
  - `validate_score()`: Compliance score range validation
  - `validate_grade()`: Grade letter validation
  - `validate_api_key()`: API key format validation

#### **Logging** (`logger_config.py`)
- Structured logging configuration
- Rotating file handlers with backup rotation
- Console and file appenders with different log levels
- Context filtering for audit trails

#### **Exception Handling** (`exceptions.py`)
- Custom exception hierarchy:
  - `ComplianceCheckerError`: Base exception
  - `ScanError`: Scanning failures
  - `NetworkError`: HTTP/connection issues
  - `InvalidURLError`: URL validation failures
  - `DatabaseError`: Database operations
  - `AIServiceError`: AI service failures
  - `ConfigurationError`: Configuration issues
  - `ValidationError`: Input validation

#### **Constants** (`constants.py`)
- Cookie banner keywords (7 patterns)
- Privacy policy keywords (4 patterns)
- Tracking domains (18+ services)
- Regex patterns for email, phone detection
- Grade thresholds (A=90, B=80, C=70, D=60)

### Scoring Algorithm

| Indicator | Points | Detection Method |
|-----------|--------|------------------|
| Cookie Consent | 30 | Banner text/ID/class patterns |
| Privacy Policy | 30 | Link href containing privacy keywords |
| Contact Info | 20 | Email regex + phone regex matching |
| Tracker Penalty | 20 | Script src matching tracking domains |

**Grade Scale:**
- A: 90+ (Excellent)
- B: 80-89 (Good)
- C: 70-79 (Fair)
- D: 60-69 (Poor)
- F: <60 (Critical)

**Status:**
- Compliant: Score ≥ 80
- Needs Improvement: Score 60-79
- Non-Compliant: Score < 60

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL or SQLite (optional, for history tracking)
- OpenAI API key (optional, for AI analysis)

### Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/GDPR-CCPA-Compilance-Checker
cd GDPR-CCPA-Compilance-Checker

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Configuration Options

See `.env.example` for all available settings:

```env
# Database (optional)
DATABASE_URL=sqlite:///compliance.db
# DATABASE_URL=postgresql://user:pass@localhost/compliance

# OpenAI (optional, for AI analysis)
OPENAI_API_KEY=sk-...

# Scoring weights (customize if needed)
SCORING_COOKIE_CONSENT=30
SCORING_PRIVACY_POLICY=30
SCORING_CONTACT_INFO=20
SCORING_TRACKERS=20

# Scanning behavior
REQUEST_TIMEOUT=10
MAX_RETRIES=3
BACKOFF_FACTOR=0.3
BATCH_SCAN_LIMIT=10
```

---

## 📊 Key Features

### Single URL Scan
- Real-time analysis with progress indicator
- Compliance score (0-100) with grade (A-F)
- Detailed findings breakdown
- AI-powered privacy policy review (if OpenAI enabled)
- Export results as CSV

### Batch Scanning
- Scan up to 10 URLs simultaneously
- Bulk export to CSV
- Error handling with invalid URL reporting
- Progress tracking

### Scan History
- Historical trend visualization
- Score improvements over time
- Access to previous scan results
- Database-backed persistence

### AI Features
- Privacy policy analysis using GPT-4o-mini
- Compliance assessment against GDPR/CCPA
- Remediation advice with implementation steps
- Risk level determination

---

## 🚀 Deployment

### Streamlit Cloud
The app is deployed at: [gdpr-ccpa-compilance-checker.streamlit.app](https://gdpr-ccpa-compilance-checker.streamlit.app/)

```bash
# Deploy with Streamlit Cloud
# 1. Push code to GitHub
# 2. Connect repository in Streamlit Cloud dashboard
# 3. Configure secrets (API keys) in the cloud console
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## 🔒 Security Considerations

### Input Validation
- All URLs validated against regex patterns
- Maximum batch size enforced (10 URLs)
- Text input sanitization (max 10,000 chars)

### API Security
- OpenAI API key stored in environment (not code)
- Database credentials in .env (not committed)
- HTTPS enforced for all external requests
- Request timeouts prevent hanging

### Error Handling
- Custom exception hierarchy for proper error routing
- Sensitive errors logged locally, generic messages to user
- Debug mode disabled in production
- Structured logging for audit trails

---

## 📈 Performance Optimizations

- **HTTP Retry Logic**: Automatic retries with exponential backoff (3 retries, 0.3s factor)
- **Connection Pooling**: Reusable sessions with persistent connections
- **Session Detachment**: Safe SQLAlchemy session handling
- **Lazy Loading Prevention**: Convert query results to dicts in context
- **Timeout Enforcement**: 10s default, configurable per request type

---

## 🧪 Testing & Validation

### Code Quality
- No syntax errors
- Type hints throughout (Python 3.10+)
- Comprehensive docstrings (Google style)
- Logging on all major operations

### Error Scenarios
- Invalid URLs (validation layer)
- Network failures (retry + timeout handling)
- Missing API keys (graceful degradation)
- Database unavailable (in-memory fallback)
- Batch too large (validation + messaging)

---

## 📝 Future Enhancements

Potential improvements for v2.0:
- [ ] Async scanning for better batch performance
- [ ] Redis caching layer for repeated scans
- [ ] Database migrations with Alembic
- [ ] Comprehensive test suite (pytest)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Rate limiting middleware
- [ ] Sentry integration for error monitoring
- [ ] API endpoint for programmatic access
- [ ] Browser extension for quick scanning

---

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ using Streamlit, BeautifulSoup4, and OpenAI**

