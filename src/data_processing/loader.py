import pandas as pd
import os

def load_data(data_dir, reference_dir):
    """Loads all CSV data and returns a dictionary of DataFrames."""
    data = {}
    
    # Load primary data
    data['assets'] = pd.read_csv(os.path.join(data_dir, 'assets.csv'))
    data['vulnerabilities'] = pd.read_csv(os.path.join(data_dir, 'vulnerabilities.csv'))
    data['threat_intel'] = pd.read_csv(os.path.join(data_dir, 'threat_intelligence.csv'))
    data['business_services'] = pd.read_csv(os.path.join(data_dir, 'business_services.csv'))
    data['remediation'] = pd.read_csv(os.path.join(data_dir, 'remediation_guidance.csv'))
    
    # Load reference data
    data['cisa_kev'] = pd.read_csv(os.path.join(reference_dir, 'cisa_kev.csv'))
    data['nist_800_53'] = pd.read_csv(os.path.join(reference_dir, 'nist_800_53.csv'))
    
    return data

def preprocess_data(data):
    """Performs basic data cleaning and preprocessing."""
    # Ensure CVE IDs are consistent (e.g., uppercase)
    data['vulnerabilities']['cve'] = data['vulnerabilities']['cve'].str.upper()
    data['threat_intel']['matched_cve_or_control'] = data['threat_intel']['matched_cve_or_control'].str.upper()
    data['cisa_kev']['cveID'] = data['cisa_kev']['cveID'].str.upper()
    
    # Fill missing values where appropriate
    data['assets']['internet_exposed'] = data['assets']['internet_exposed'].fillna('No')
    data['assets']['criticality'] = data['assets']['criticality'].fillna('Medium')
    
    return data
