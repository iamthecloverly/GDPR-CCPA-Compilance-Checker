# GDPR/CCPA Compliance Checker

A modern, AI-assisted privacy compliance scanner for quick GDPR/CCPA signals and audit-ready exports.

**Live demo:** https://gdpr-ccpa-compilance-checker.streamlit.app/

## Why it matters (recruiter summary)

This project turns privacy compliance checks into a fast, repeatable workflow. It automates discovery of cookie consent banners, privacy policy links, contact info, and third‑party trackers, then summarizes risk with a clear score, grade, and recommendations. The result is a lightweight tool that helps teams prioritize privacy fixes and create shareable reports in minutes.

## What I built

- Single and batch scanning with clear scoring and exportable CSV reports.
- AI‑assisted policy review that highlights strengths, gaps, and remediation steps.
- Historical tracking with score trends (database‑backed) for ongoing monitoring.

## What I learned (short)

- Building reliable web scraping with retries, timeouts, and HTML validation.
- Designing a production‑ready Streamlit UI with glassmorphism and performance‑friendly styling.
- Structuring a clean MVC‑style Python app and integrating external AI services safely.

## Quick start

```bash
pip install .
streamlit run app.py
```

## Configuration

```bash
export DATABASE_URL="sqlite:///compliance.db"
export OPENAI_API_KEY="sk-..."  # optional
```

## License

Add your project license information here.
