# GDPR/CCPA Compliance Checker

The GDPR/CCPA Compliance Checker is a Streamlit application that scans public webpages for common privacy compliance indicators. It highlights issues related to cookie consent, privacy policies, third-party trackers, and contact information, and it can optionally leverage OpenAI models for deeper policy analysis and remediation advice.

## Key Features

- **Single-site scans with compliance scoring** – Inspect a single URL to detect cookie consent banners, privacy policy links, contact information, and third-party trackers. Results are summarized in a weighted compliance score with grade and status indicators.【F:app.py†L53-L154】【F:controllers/compliance_controller.py†L12-L89】
- **AI-assisted policy review (optional)** – When an OpenAI API key is configured, the tool downloads the detected privacy policy, evaluates it for GDPR/CCPA coverage, and surfaces strengths, gaps, and actionable recommendations.【F:services/openai_service.py†L1-L133】【F:app.py†L220-L331】
- **Historical tracking and trends** – Persist scan results in a SQL database to view history, score trends, and changes in compliance posture over time.【F:app.py†L333-L404】【F:database/operations.py†L1-L88】
- **Batch scanning** – Submit multiple URLs at once to compare privacy readiness across sites, complete with summary metrics and CSV exports.【F:app.py†L406-L491】
- **Exportable reports** – Generate CSV summaries for single scans or batch results for auditing and sharing.【F:app.py†L114-L146】【F:app.py†L471-L490】

## Architecture Overview

The application follows a lightweight MVC pattern:

- **Streamlit UI (`app.py`)** handles inputs, visualization, and report generation.
- **Controller (`controllers/compliance_controller.py`)** orchestrates scans and aggregates results.
- **Model (`models/compliance_model.py`)** fetches webpages and detects privacy artefacts such as cookie banners, trackers, privacy policies, and contact info.【F:models/compliance_model.py†L1-L171】
- **Services (`services/openai_service.py`)** integrate with OpenAI for AI analysis and recommendations.
- **Persistence layer (`database/`)** stores scan metadata using SQLAlchemy models and operations.【F:database/models.py†L1-L53】【F:database/operations.py†L1-L88】

## Prerequisites

- Python 3.11 or newer.【F:pyproject.toml†L1-L16】
- A reachable SQL database. For local testing you can use SQLite by pointing `DATABASE_URL` to a file (e.g., `sqlite:///compliance.db`).【F:database/db.py†L1-L27】
- Optional: an OpenAI API key to enable AI-powered analysis (`OPENAI_API_KEY`).【F:services/openai_service.py†L1-L82】

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-org>/GDRP-CCPA-Compilance-Checker.git
   cd GDRP-CCPA-Compilance-Checker
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install .
   ```
   Alternatively, use a modern dependency manager such as [uv](https://docs.astral.sh/uv/) or `pip-tools` to sync from
   `pyproject.toml` if you prefer locked installations.

## Configuration

Set the required environment variables before launching the app:

```bash
export DATABASE_URL="sqlite:///compliance.db"  # or your preferred database
export OPENAI_API_KEY="sk-..."                  # optional, enables AI analysis
```

On Windows PowerShell, use:

```powershell
$env:DATABASE_URL="sqlite:///compliance.db"
$env:OPENAI_API_KEY="sk-..."
```

The first run will automatically create the database schema.【F:database/db.py†L11-L27】【F:database/models.py†L1-L25】

## Usage

1. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

2. Open the provided URL in your browser. From the UI you can:
   - Perform a **Single Scan** by entering a URL and optionally enabling AI analysis.
   - Review **Scan History** to visualize compliance trends for previously scanned sites.
   - Run a **Batch Scan** on up to 10 URLs and compare their results side by side.【F:app.py†L53-L493】

3. Download CSV reports from the results view for documentation or further analysis.【F:app.py†L114-L146】【F:app.py†L471-L490】

## Development Tips

- The model layer makes HTTP requests and parses HTML; ensure outbound network access is permitted when running scans.【F:models/compliance_model.py†L1-L171】
- AI functionality gracefully degrades when `OPENAI_API_KEY` is not set, returning clear error messages to the UI.【F:services/openai_service.py†L15-L81】【F:app.py†L213-L220】
- Database operations use SQLAlchemy sessions with automatic commit/rollback helpers via `get_db()` context manager.【F:database/db.py†L11-L27】【F:database/operations.py†L1-L88】

## License

Add your project license information here.
