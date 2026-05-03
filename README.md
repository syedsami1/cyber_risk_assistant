# AI-Powered Cyber Risk Assistant

## Project Overview

This project develops an AI-powered cyber risk assistant designed to help organizations prioritize and understand their cybersecurity risks. It ingests various data sources, identifies and ranks top risks, correlates vulnerabilities with threat intelligence, maps risks to assets and business services, generates human-readable risk explanations, and retrieves relevant NIST SP 800-53 Rev. 5 controls using a Retrieval-Augmented Generation (RAG) approach.

## Architecture

The system is composed of several key modules:

1.  **Data Ingestion & Preprocessing**: Handles loading and cleaning of raw CSV data (assets, vulnerabilities, threat intelligence, business services, remediation guidance) and the synthetic threat report. It also integrates external data sources like the CISA KEV catalog and NIST SP 800-53 controls.
2.  **Risk Scoring Engine**: Implements a multi-factor risk scoring mechanism that goes beyond simple CVSS scores. Factors considered include internet exposure, active exploit availability, threat actor campaign matches, business service criticality, and missing compensating controls.
3.  **Threat Intelligence Correlation**: Correlates identified vulnerabilities with active threat intelligence, including ransomware campaigns, to provide a more accurate risk picture.
4.  **NIST SP 800-53 RAG Retrieval**: Utilizes a RAG pipeline with open-source embeddings and a vector database (e.g., ChromaDB/FAISS) to retrieve and summarize relevant NIST SP 800-53 Rev. 5 controls for each identified risk.
5.  **LLM Integration (Groq API)**: Leverages the Groq API for generating clear, human-readable explanations for each risk and summarizing NIST control guidance.
6.  **Streamlit UI**: Provides a simple, clean, and interactive web interface to display the top 5 ranked risks, their explanations, and associated NIST control guidance.

## Setup and Run

To set up and run the Cyber Risk Assistant, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/syedsami1/cyber_risk_assistant.git
    cd cyber_risk_assistant
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up Groq API Key:**
    Obtain a Groq API key from [Groq Console](https://console.groq.com/).
    Set it as an environment variable:
    ```bash
    export GROQ_API_KEY="your_groq_api_key"
    ```
    Alternatively, you can enter it directly in the Streamlit UI sidebar.

4.  **Run the Streamlit application:**
    ```bash
    streamlit run src/ui/app.py
    ```

    The application will open in your web browser, typically at `http://localhost:8501`.

## Supporting Questions

### Q1: The data split

**Embedded Data:** The NIST SP 800-53 Rev. 5 controls (`nist_800_53.csv`) are embedded into a ChromaDB vector store. This is because the NIST controls contain rich, descriptive text that benefits from semantic search. Embedding allows the system to retrieve controls that are conceptually similar to a given query, even if exact keywords are not present, which is crucial for RAG-based guidance retrieval.

**Structured Data:** The `assets.csv`, `vulnerabilities.csv`, `threat_intelligence.csv`, `business_services.csv`, `remediation_guidance.csv`, and `cisa_kev.csv` are treated as structured records. These datasets contain discrete, categorical, and numerical information (e.g., CVSS scores, asset criticality, boolean flags for internet exposure or ransomware association) that are best queried and joined using traditional DataFrame operations. This approach allows for precise filtering, merging, and numerical calculations required for multi-factor risk scoring.


### Q2: Where it goes wrong

1.  **Incomplete or Outdated CISA KEV Data**: If a CVE ID in `vulnerabilities.csv` has no matching entry in the CISA KEV catalog (`cisa_kev.csv`), my system will not flag it as actively exploited or ransomware-associated, even if it is. This could lead to under-prioritization of critical vulnerabilities. To mitigate this, the system could incorporate multiple threat intelligence feeds or regularly update the CISA KEV data from its source.
2.  **Ambiguous NIST Control Retrieval**: The RAG system relies on the quality of the query and the embeddings. If the query for NIST controls is too generic or the embeddings fail to capture the nuanced context of a vulnerability, the system might retrieve less relevant controls. This could be addressed by refining the query generation logic to include more specific vulnerability and asset details, or by experimenting with different embedding models and fine-tuning the retriever.
3.  **LLM Hallucination in Explanations**: While Groq is powerful, LLMs can occasionally "hallucinate" or provide plausible but incorrect explanations, especially if the input data is contradictory or ambiguous. This could lead to misleading risk explanations or remediation summaries. A human-in-the-loop review process for the generated explanations would be ideal. Additionally, implementing guardrails or fact-checking mechanisms within the LLM prompt engineering could help reduce such occurrences.


### Q3: One thing you would change

If I had another day, the single most important thing I would improve is the **dynamic weighting and configurability of the risk scoring model**. Currently, the risk scoring logic has hardcoded weights for various factors (e.g., +2 for internet exposure, +4 for ransomware association). While these are based on the problem statement's guidance, a more robust system would allow security analysts to dynamically adjust these weights, add new factors, or even define custom scoring rules through the UI. This would enable the assistant to adapt to an organization's evolving risk appetite and specific operational context without requiring code changes, making it significantly more flexible and valuable in a real-world scenario.
