import os
from groq import Groq

class GroqRiskAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            # For local testing if key is not set, we might need to handle it
            pass
        self.client = Groq(api_key=self.api_key)

    def generate_risk_explanation(self, risk_details):
        """Generates a plain-English explanation for why a risk is ranked highly."""
        prompt = f"""
        You are a senior cybersecurity risk analyst. 
        Explain why the following vulnerability on this specific asset is a top priority risk.
        
        Details:
        - Asset: {risk_details['asset_name']} ({risk_details['asset_type']})
        - Vulnerability: {risk_details['cve_id']} (CVSS: {risk_details['cvss_score']})
        - Internet Exposed: {risk_details['internet_exposure_vuln']}
        - In CISA KEV: {risk_details['is_kev']}
        - Ransomware Associated: {risk_details['is_ransomware']}
        - Threat Intel Match: {risk_details['is_threat_intel_match']}
        - Business Service: {risk_details['business_service']} (Criticality: {risk_details['criticality']})
        - Risk Score: {risk_details['risk_score']}
        
        Provide a concise, professional, plain-English sentence explaining the ranking.
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content.strip()

    def summarize_nist_guidance(self, risk_details, nist_controls):
        """Summarizes NIST guidance for a specific risk."""
        controls_text = "\n\n".join(nist_controls)
        prompt = f"""
        Based on the following NIST SP 800-53 controls, provide a brief, actionable remediation summary for this risk:
        
        Risk: {risk_details['cve_id']} on {risk_details['asset_name']}
        
        NIST Controls:
        {controls_text}
        
        Provide a short summary of what NIST recommends for this specific scenario.
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content.strip()
