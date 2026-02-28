"""Medical disclaimer component."""

import streamlit as st


def show_disclaimer():
    """Show and manage disclaimer acceptance."""
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False
    
    if st.session_state.disclaimer_accepted:
        return True
    
    with st.container():
        st.warning("""
        ⚠️ **IMPORTANT MEDICAL DISCLAIMER**
        
        This application is for **educational and informational purposes only**.
        
        - This is NOT a substitute for professional medical advice, diagnosis, or treatment
        - Always seek the advice of your physician or other qualified health provider
        - Never disregard professional medical advice because of information you read here
        - In case of emergency, call your local emergency number immediately
        
        By using this application, you acknowledge that you understand these limitations.
        """)
        
        accepted = st.checkbox("I have read and understand the disclaimer above")
        
        if accepted:
            st.session_state.disclaimer_accepted = True
            st.rerun()
        
        return False