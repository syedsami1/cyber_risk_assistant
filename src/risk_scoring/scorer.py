import pandas as pd

def calculate_risk_scores(data):
    """Calculates risk scores for each vulnerability-asset pair."""
    vulns = data['vulnerabilities']
    assets = data['assets']
    threat_intel = data['threat_intel']
    cisa_kev = data['cisa_kev']
    business_services = data['business_services']

    # Merge vulnerabilities with asset information
    merged = pd.merge(vulns, assets, on='asset_id', how='left', suffixes=('_vuln', '_asset'))

    # Merge with business services to get criticality
    merged = pd.merge(merged, business_services, left_on='business_service', right_on='business_service', how='left')

    # Mark vulnerabilities in CISA KEV
    merged['is_kev'] = merged['cve'].isin(cisa_kev['cveID'])
    
    # Check for ransomware association in KEV
    kev_ransomware = cisa_kev[cisa_kev['knownRansomwareCampaignUse'] == 'Known']['cveID']
    merged['is_ransomware'] = merged['cve'].isin(kev_ransomware)

    # Check for matches in threat intelligence
    merged['is_threat_intel_match'] = merged['cve'].isin(threat_intel['matched_cve_or_control'])

    # Scoring Logic
    # Base Score: CVSS
    merged['risk_score'] = merged['cvss']

    # Multipliers/Add-ons based on factors
    # 1. Internet Exposure: +2 if exposed
    merged.loc[merged['internet_exposed'] == 'Yes', 'risk_score'] += 2
    
    # 2. Active Exploitation (KEV): +3 if in KEV
    merged.loc[merged['is_kev'], 'risk_score'] += 3
    
    # 3. Ransomware Association: +4 if known ransomware use
    merged.loc[merged['is_ransomware'], 'risk_score'] += 4
    
    # 4. Threat Intel Match: +2 if matched in threat intel
    merged.loc[merged['is_threat_intel_match'], 'risk_score'] += 2
    
    # 5. Business Criticality: High/Critical +2
    merged.loc[merged['criticality'].isin(['High', 'Critical']), 'risk_score'] += 2
    
    # 6. Missing EDR: +1 if EDR not enabled
    merged.loc[merged['edr_installed'] == 'No', 'risk_score'] += 1

    # Rank and select top 5
    top_5_risks = merged.sort_values(by='risk_score', ascending=False).head(5)
    
    return top_5_risks
