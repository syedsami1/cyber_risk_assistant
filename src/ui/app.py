import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processing.loader import load_data, preprocess_data
from risk_scoring.scorer import calculate_risk_scores
from rag_nist.retriever import NISTRetriever
from llm_integration.groq_client import GroqRiskAssistant

st.set_page_config(page_title="TawasolPay Cyber Risk Assistant", layout="wide")

st.title("🛡️ AI-Powered Cyber Risk Assistant")
st.markdown("### Top 5 Prioritized Cybersecurity Risks for TawasolPay")

# Sidebar for configuration
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")

# Use relative paths from the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
data_dir = os.path.join(BASE_DIR, 'data')
ref_dir = os.path.join(BASE_DIR, 'data') # In the new structure, they are in the same folder

@st.cache_resource
def init_retriever():
    nist_path = os.path.join(ref_dir, 'nist_800_53.csv')
    # Use a relative path for chroma_db as well
    persist_dir = os.path.join(BASE_DIR, 'chroma_db')
    return NISTRetriever(nist_path, persist_directory=persist_dir)

if not groq_api_key:
    st.warning("Please enter your Groq API Key in the sidebar to generate AI explanations.")
else:
    try:
        # Load and process data
        with st.spinner("Analyzing data..."):
            raw_data = load_data(data_dir, ref_dir)
            processed_data = preprocess_data(raw_data)
            top_risks = calculate_risk_scores(processed_data)
            
            retriever = init_retriever()
            groq_assistant = GroqRiskAssistant(api_key=groq_api_key)

        # Display Top 5 Risks
        for idx, (i, row) in enumerate(top_risks.iterrows()):
            with st.expander(f"Risk #{idx+1}: {row['cve']} on {row['asset_name']} (Score: {row['risk_score']:.1f})", expanded=True):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### Risk Context")
                    st.write(f"**Asset:** {row['asset_name']} ({row['asset_type']})")
                    st.write(f"**Business Service:** {row['business_service']}")
                    st.write(f"**Criticality:** {row['criticality']}")
                    st.write(f"**Internet Exposed:** {row['internet_exposed']}")
                    st.write(f"**CVSS Score:** {row['cvss']}")
                    
                    # Prepare details for AI
                    risk_details = {
                        'asset_name': row['asset_name'],
                        'asset_type': row['asset_type'],
                        'cve_id': row['cve'],
                        'cvss_score': row['cvss'],
                        'internet_exposure_vuln': row['internet_exposed'],
                        'is_kev': row['is_kev'],
                        'is_ransomware': row['is_ransomware'],
                        'is_threat_intel_match': row['is_threat_intel_match'],
                        'business_service': row['business_service'],
                        'criticality': row['criticality'],
                        'risk_score': row['risk_score']
                    }
                    
                    # AI Explanation
                    st.markdown("#### AI Risk Explanation")
                    explanation = groq_assistant.generate_risk_explanation(risk_details)
                    st.info(explanation)

                with col2:
                    st.markdown("#### NIST SP 800-53 Remediation")
                    # RAG Retrieval
                    query = f"Remediation for {row['cve']} on {row['asset_type']} exposed to internet"
                    nist_results = retriever.retrieve_controls(query)
                    
                    controls_docs = nist_results['documents'][0]
                    summary = groq_assistant.summarize_nist_guidance(risk_details, controls_docs)
                    st.success(summary)
                    
                    with st.expander("View Source NIST Controls"):
                        for i, ctrl in enumerate(nist_results['metadatas'][0]):
                            st.markdown(f"**{ctrl['identifier']}: {ctrl['name']}**")
                            st.text(controls_docs[i])

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)
