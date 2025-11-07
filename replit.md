# GDPR/CCPA Compliance Checker

## Overview

This application is a web-based privacy compliance scanner that analyzes websites for GDPR and CCPA regulatory compliance. It crawls target websites to detect cookie consent mechanisms, privacy policies, contact information, and third-party trackers, then provides actionable compliance recommendations. The tool uses web scraping to extract compliance artifacts and optionally leverages OpenAI's API for intelligent privacy policy analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### MVC Architecture Pattern

The application follows a Model-View-Controller (MVC) design pattern to separate concerns:

**Problem Addressed:** Need for clean separation between data extraction, business logic, and presentation layers.

**Solution:** Three-tier MVC architecture where:
- **Model** (`models/compliance_model.py`): Handles web scraping, HTML parsing, and data extraction
- **Controller** (`controllers/compliance_controller.py`): Orchestrates the scanning workflow, coordinates between model and services, calculates compliance summaries
- **View** (`app.py`): Streamlit-based UI for user interaction and results presentation

**Rationale:** This separation allows independent evolution of scanning logic, analysis workflows, and UI without tight coupling. The controller acts as a coordination layer that can easily integrate new compliance checks or analysis services.

### Web Scraping Layer

**Technology:** BeautifulSoup4 with lxml parser and Requests library

**Problem Addressed:** Need to extract compliance-related artifacts from arbitrary websites.

**Solution:** The ComplianceModel class fetches HTML content and uses BeautifulSoup to parse and search for:
- Cookie consent banners (via keyword matching and DOM element detection)
- Privacy policy links (via anchor text and href patterns)
- Contact information (email addresses, forms)
- Third-party tracking scripts

**Design Decision:** Pattern-based detection using keyword lists and CSS class matching rather than computer vision or screenshot analysis, balancing accuracy with performance and simplicity.

### AI Analysis Service

**Technology:** OpenAI API with Trafilatura for content extraction

**Problem Addressed:** Privacy policies are lengthy legal documents that require semantic understanding to assess compliance.

**Solution:** A dedicated service layer (`services/openai_service.py`) that:
1. Uses Trafilatura to extract clean text from privacy policy URLs
2. Sends truncated policy text (8000 characters) to OpenAI for analysis
3. Receives structured compliance assessment for GDPR/CCPA requirements

**Alternatives Considered:** 
- Rule-based keyword matching (insufficient for complex legal language)
- Custom ML model (requires training data and maintenance)

**Chosen Approach:** OpenAI API provides robust semantic analysis without model maintenance overhead. Content is truncated to manage API costs while capturing essential policy sections.

### Compliance Scoring System

**Implementation:** The controller calculates a weighted compliance score based on multiple compliance categories:
- Cookie Consent Banner (30% weight)
- Privacy Policy Completeness (40% weight)
- Tracker Management (20% weight)
- Contact Information (10% weight)

**Design Decision - Updated (November 2025):** Migrated from simple boolean checks to a weighted scoring system (0-100 scale with letter grades A-F) to provide more nuanced compliance assessment. Each category is scored individually, then multiplied by its weight to calculate an overall compliance score. This approach better reflects the relative importance of different privacy requirements.

**Tracker Scoring Logic:**
- 0 trackers = 100 points
- 1-3 trackers = 70 points  
- 4-6 trackers = 40 points
- 7+ trackers = 20 points

### Frontend Architecture

**Technology:** Streamlit

**Problem Addressed:** Need for rapid deployment of an interactive web interface without complex frontend development.

**Solution:** Streamlit provides declarative UI components with built-in state management, allowing the entire interface to be defined in a single Python file.

**Pros:**
- Rapid prototyping and deployment
- No separate frontend stack required
- Python-native development

**Cons:**
- Limited customization compared to React/Vue
- Stateful interactions can be complex
- Not ideal for high-traffic production applications

## External Dependencies

### Third-Party Libraries

- **Streamlit**: Web application framework for the user interface
- **BeautifulSoup4** (lxml parser): HTML parsing and DOM traversal for compliance artifact detection
- **Requests**: HTTP client for fetching website content
- **Trafilatura**: Content extraction from web pages, specifically for cleaning privacy policy text
- **OpenAI Python SDK**: Integration with OpenAI's GPT models for privacy policy semantic analysis

### External APIs

- **OpenAI API**: Used for intelligent analysis of privacy policy documents to assess GDPR and CCPA compliance. Requires `OPENAI_API_KEY` environment variable.

### Configuration Requirements

- **OPENAI_API_KEY**: Environment variable must be set for AI-powered privacy policy analysis. Application degrades gracefully if not configured, returning error messages instead of analysis results.

### Data Storage

**Technology:** PostgreSQL database with SQLAlchemy ORM

**Problem Addressed:** Need to track compliance changes over time and provide historical trend analysis.

**Solution - Updated (November 2025):** The application now uses a PostgreSQL database to persist scan results. The database schema (`database/models.py`) stores:
- Complete scan results including all compliance metrics
- Weighted category scores (cookie consent, privacy policy, trackers, contact info)
- AI analysis results (GDPR/CCPA compliance, detected trackers)
- Scan timestamps for trend tracking

**Database Operations** (`database/operations.py`):
- `save_scan_result()`: Persists each scan with full compliance data
- `get_scan_history()`: Retrieves historical scans for a specific URL
- `get_score_trend()`: Calculates compliance score trends over time
- `get_all_scanned_urls()`: Returns list of all previously scanned websites

**Rationale:** Persistence enables users to track compliance improvements or degradations over time, compare scan results, and analyze trends. The database layer uses SQLAlchemy for database abstraction and includes transaction management through context managers.

### Enhanced Features (November 2025)

**Tracker Detection Database:** Expanded from 10 to 35+ third-party tracking services and consent management platforms, including:
- Analytics: Google Analytics, Mixpanel, Amplitude, Heap, Adobe Analytics, Matomo
- Social Media Pixels: Facebook, Twitter/X, LinkedIn, Pinterest, TikTok, Snapchat
- Heatmapping/Session Recording: Hotjar, Crazy Egg, Mouseflow, Lucky Orange, Microsoft Clarity, FullStory
- A/B Testing: Optimizely, VWO
- Consent Management: OneTrust, Cookiebot, Termly, Osano, Usercentrics, Didomi
- Other: Segment, HubSpot, Intercom, Salesforce, Quantcast, Plausible, Fathom

**CSV Export:** Users can download comprehensive compliance reports as CSV files containing:
- Overall compliance score, grade, and status
- Category breakdown with weighted scores
- Cookie banner detection details
- Tracking script inventory
- Privacy policy analysis results (GDPR/CCPA compliance, compliance checklist)
- AI-generated priority actions and recommendations

**Batch Scanning:** The application supports scanning multiple websites simultaneously (up to 10 URLs) with:
- Parallel processing with progress tracking
- Comparison dashboard showing aggregate metrics
- Average compliance scores across scanned sites
- Downloadable batch results in CSV format

**Historical Tracking:** Users can view compliance trends over time including:
- Line charts showing overall score progression
- Category-specific trend visualization (cookie, privacy, trackers)
- Tabular scan history with GDPR/CCPA compliance status
- Delta indicators showing score changes between scans