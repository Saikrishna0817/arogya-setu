"""Main Streamlit application entry point."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from config.languages import LANG_CONFIG

# Page configuration
st.set_page_config(
    page_title="Vernacular Medical Parser",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize settings
Settings.ensure_dirs()


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'ocr_engine': None,
        'parser': None,
        'llm_client': None,
        'translator': None,
        'tts_engine': None,
        'vault_manager': None,
        'current_prescription': None,
        'current_explanation': None,
        'current_audio': None,
        'disclaimer_accepted': False,
        'patient_context': {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def show_disclaimer():
    """Show medical disclaimer."""
    if st.session_state.disclaimer_accepted:
        return True
    
    st.warning("""
    ⚠️ **Medical Disclaimer**
    
    This application is for educational purposes only. It does not provide medical advice, 
    diagnosis, or treatment. Always seek the advice of your physician or other qualified 
    health provider with any questions you may have regarding a medical condition.
    
    **Do not disregard professional medical advice or delay seeking it because of 
    information provided by this application.**
    """)
    
    if st.checkbox("I understand and agree to these terms"):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    
    return False


def main():
    """Main application."""
    init_session_state()
    
    st.title("🏥 Vernacular Medical Prescription Parser")
    st.markdown("*Making medical prescriptions accessible to everyone*")
    
    # Show disclaimer first
    if not show_disclaimer():
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    pages = {
        "Prescription Parser": "pages/prescription_parser",
        "Lab Report Analyzer": "pages/lab_report_agent",
        "Drug Interaction Check": "pages/drug_interaction",
        "Dosage Validator": "pages/dosage_anomaly",
        "Medication Schedule": "pages/medication_schedule",
        "Prescription History": "pages/prescription_vault",
        "Chronic Patient Mode": "pages/chronic_patient_mode"
    }
    
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    
    # Import and show selected page
    page_module = pages[selection]
    
    if selection == "Prescription Parser":
        from app.pages import prescription_parser
        prescription_parser.show()
    elif selection == "Lab Report Analyzer":
        from app.pages import lab_report_agent
        lab_report_agent.show()
    elif selection == "Drug Interaction Check":
        from app.pages import drug_interaction
        drug_interaction.show()
    elif selection == "Dosage Validator":
        from app.pages import dosage_anomaly
        dosage_anomaly.show()
    elif selection == "Medication Schedule":
        from app.pages import medication_schedule
        medication_schedule.show()
    elif selection == "Prescription History":
        from app.pages import prescription_vault
        prescription_vault.show()
    elif selection == "Chronic Patient Mode":
        from app.pages import chronic_patient_mode
        chronic_patient_mode.show()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("© 2024 Vernacular Medical Parser")


if __name__ == "__main__":
    main()