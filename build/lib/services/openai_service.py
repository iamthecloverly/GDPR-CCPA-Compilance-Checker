import json
import os
from openai import OpenAI
import trafilatura

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None


def _get_openai_client():
    global openai_client
    if openai_client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return openai_client


def analyze_privacy_policy(privacy_url: str) -> dict:
    try:
        client = _get_openai_client()
    except ValueError as e:
        return {
            'error': 'AI analysis unavailable: OpenAI API key not configured',
            'gdpr_compliant': False,
            'ccpa_compliant': False
        }
    
    try:
        downloaded = trafilatura.fetch_url(privacy_url)
        if not downloaded:
            return {
                'error': 'Failed to fetch privacy policy content',
                'compliant': False
            }
        
        text = trafilatura.extract(downloaded)
        
        if not text or len(text) < 100:
            return {
                'error': 'Privacy policy content too short or unavailable',
                'compliant': False
            }
        
        truncated_text = text[:8000]
        
        prompt = f"""Analyze this privacy policy for GDPR and CCPA compliance. 

Privacy Policy Content:
{truncated_text}

Provide a JSON response with the following structure:
{{
    "gdpr_compliant": true/false,
    "ccpa_compliant": true/false,
    "overall_compliance_score": 0-100,
    "data_collection_mentioned": true/false,
    "data_deletion_rights": true/false,
    "data_sharing_disclosed": true/false,
    "user_consent_mechanism": true/false,
    "contact_information_provided": true/false,
    "cookie_usage_explained": true/false,
    "third_party_disclosure": true/false,
    "missing_elements": ["list of missing compliance elements"],
    "strengths": ["list of compliance strengths"],
    "summary": "brief summary of compliance status"
}}"""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a privacy compliance expert specializing in GDPR and CCPA regulations. Analyze privacy policies and provide detailed compliance assessments in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        content = response.choices[0].message.content
        if not content or content.strip() == "":
            return {
                'error': 'AI returned empty response',
                'gdpr_compliant': False,
                'ccpa_compliant': False
            }
        
        result = json.loads(content)
        return result
        
    except Exception as e:
        return {
            'error': f'AI analysis failed: {str(e)}',
            'compliant': False
        }


def get_compliance_recommendations(scan_results: dict) -> dict:
    try:
        client = _get_openai_client()
    except ValueError as e:
        return {
            'error': 'AI recommendations unavailable: OpenAI API key not configured'
        }
    
    try:
        prompt = f"""Based on this website compliance scan, provide actionable recommendations for improving GDPR/CCPA compliance.

Scan Results:
- Cookie Banner Detected: {scan_results.get('cookie_banner', {}).get('detected', False)}
- Tracking Scripts Found: {scan_results.get('tracking_scripts', {}).get('total_trackers', 0)}
- Trackers: {', '.join(scan_results.get('tracking_scripts', {}).get('tracker_names', []))}
- Privacy Policy Found: {scan_results.get('privacy_policy', {}).get('found', False)}
- Contact Information: {scan_results.get('contact_info', {}).get('detected', False)}

Provide a JSON response with:
{{
    "priority_actions": ["list of high-priority actions"],
    "suggested_improvements": ["list of recommended improvements"],
    "compliance_risks": ["list of potential compliance risks"],
    "overall_assessment": "brief overall assessment"
}}"""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a privacy compliance consultant. Provide practical, actionable recommendations for website owners to improve their GDPR/CCPA compliance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=1500
        )
        
        content = response.choices[0].message.content
        if not content or content.strip() == "":
            return {
                'error': 'AI returned empty response'
            }
        
        result = json.loads(content)
        return result
        
    except Exception as e:
        return {
            'error': f'Failed to generate recommendations: {str(e)}'
        }
