
from fpdf import FPDF
from datetime import datetime
import io

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'GDPR/CCPA Compliance Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(url, results, ai_analysis=None):
    pdf = PDFReport()
    pdf.add_page()

    # Metadata
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Target URL: {url}", ln=True)
    pdf.cell(0, 10, f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Score & Grade
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(0, 10, f"Compliance Score: {results['score']}/100", ln=True)
    pdf.cell(0, 10, f"Grade: {results['grade']}", ln=True)
    pdf.cell(0, 10, f"Status: {results['status']}", ln=True)
    pdf.ln(10)

    # Detailed Findings
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(0, 10, "Detailed Findings:", ln=True)
    pdf.set_font("Arial", size=11)

    findings = [
        f"Cookie Consent: {results.get('cookie_consent', 'N/A')}",
        f"Privacy Policy: {results.get('privacy_policy', 'N/A')}",
        f"CCPA Compliance: {results.get('ccpa_compliance', 'N/A')}",
        f"Contact Info: {results.get('contact_info', 'N/A')}",
        f"Trackers Found: {len(results.get('trackers', []))}"
    ]

    for item in findings:
        pdf.cell(0, 8, item, ln=True)

    if results.get('trackers'):
        pdf.ln(5)
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Detected Trackers:", ln=True)
        pdf.set_font("Arial", size=10)
        for tracker in results['trackers']:
            pdf.cell(0, 6, f"- {tracker}", ln=True)

    # AI Analysis
    if ai_analysis:
        pdf.ln(10)
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(0, 10, "AI Analysis:", ln=True)
        pdf.set_font("Arial", size=10)

        # Handle markdown-like text from AI (basic cleanup)
        clean_analysis = ai_analysis.replace("**", "").replace("* ", "- ")
        pdf.multi_cell(0, 6, clean_analysis)

    return pdf.output(dest='S').encode('latin-1', 'replace')
