"""Drug interaction checker page."""

import streamlit as st
from core.interaction.interaction_checker import InteractionChecker


def show():
    """Show drug interaction page."""
    st.header("⚠️ Drug Interaction Checker")
    st.markdown("Check for interactions between medications.")
    
    # Input method
    method = st.radio("Input method", ["Enter manually", "From prescription"])
    
    drugs = []
    
    if method == "Enter manually":
        drug_input = st.text_area("Enter drug names (one per line)")
        drugs = [d.strip() for d in drug_input.split('\n') if d.strip()]
    else:
        if st.session_state.current_prescription:
            drugs = [
                m.name for m in st.session_state.current_prescription.medications
            ]
            st.info(f"Loaded {len(drugs)} drugs from current prescription")
        else:
            st.warning("No prescription loaded. Please parse a prescription first.")
    
    if drugs and st.button("Check Interactions"):
        checker = InteractionChecker()
        
        with st.spinner("Checking..."):
            # Create medication dicts
            med_dicts = [{'name': d} for d in drugs]
            result = checker.check_prescription(med_dicts)
        
        if result['interactions_found']:
            st.error(f"Found {result['total_interactions']} interaction(s)!")
            
            for severity, interactions in result['by_severity'].items():
                if interactions:
                    with st.expander(f"{severity.upper()} ({len(interactions)})"):
                        for inter in interactions:
                            st.markdown(f"""
                            **{inter['drug1']} + {inter['drug2']}**
                            - Severity: {inter.get('severity', 'Unknown')}
                            - Description: {inter.get('description', 'No details')}
                            """)
        else:
            st.success("No significant interactions found.")
        
        if result['recommendations']:
            st.subheader("Recommendations")
            for rec in result['recommendations']:
                st.info(rec)