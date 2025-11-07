from models.compliance_model import ComplianceModel
from services.openai_service import analyze_privacy_policy, get_compliance_recommendations
from typing import Dict


class ComplianceController:
    def __init__(self, url: str):
        self.url = url
        self.model = ComplianceModel(url)
        self.results = {}
    
    def run_scan(self, include_ai_analysis: bool = True) -> Dict:
        self.results = self.model.run_all()
        
        if 'error' in self.results:
            return self.results
        
        if include_ai_analysis:
            privacy_policy = self.results.get('privacy_policy', {})
            
            if privacy_policy.get('found') and privacy_policy.get('links'):
                policy_url = privacy_policy['links'][0]['url']
                
                ai_analysis = analyze_privacy_policy(policy_url)
                self.results['policy_analysis'] = ai_analysis
            else:
                self.results['policy_analysis'] = {
                    'error': 'No privacy policy found to analyze',
                    'gdpr_compliant': False,
                    'ccpa_compliant': False
                }
            
            recommendations = get_compliance_recommendations(self.results)
            self.results['recommendations'] = recommendations
        
        self.results['compliance_summary'] = self._calculate_compliance_summary()
        
        return self.results
    
    def _calculate_compliance_summary(self) -> Dict:
        weights = {
            'cookie_consent': 0.30,
            'privacy_policy': 0.40,
            'trackers': 0.20,
            'contact_info': 0.10
        }
        
        scores = {}
        
        cookie_banner = self.results.get('cookie_banner', {})
        if cookie_banner.get('detected'):
            scores['cookie_consent'] = 100
        else:
            scores['cookie_consent'] = 0
        
        privacy_policy = self.results.get('privacy_policy', {})
        policy_analysis = self.results.get('policy_analysis', {})
        
        if privacy_policy.get('found'):
            if not policy_analysis.get('error'):
                ai_score = policy_analysis.get('overall_compliance_score', 0)
                scores['privacy_policy'] = ai_score
            else:
                scores['privacy_policy'] = 50
        else:
            scores['privacy_policy'] = 0
        
        tracking = self.results.get('tracking_scripts', {})
        total_trackers = tracking.get('total_trackers', 0)
        if total_trackers == 0:
            scores['trackers'] = 100
        elif total_trackers <= 3:
            scores['trackers'] = 70
        elif total_trackers <= 6:
            scores['trackers'] = 40
        else:
            scores['trackers'] = 20
        
        contact_info = self.results.get('contact_info', {})
        if contact_info.get('detected'):
            scores['contact_info'] = 100
        else:
            scores['contact_info'] = 0
        
        weighted_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        if weighted_score >= 75:
            status = 'Excellent'
            color = 'green'
            grade = 'A'
        elif weighted_score >= 65:
            status = 'Good'
            color = 'green'
            grade = 'B'
        elif weighted_score >= 50:
            status = 'Fair'
            color = 'orange'
            grade = 'C'
        elif weighted_score >= 35:
            status = 'Poor'
            color = 'orange'
            grade = 'D'
        else:
            status = 'Critical'
            color = 'red'
            grade = 'F'
        
        return {
            'weighted_score': round(weighted_score, 1),
            'category_scores': scores,
            'weights': weights,
            'status': status,
            'color': color,
            'grade': grade
        }
