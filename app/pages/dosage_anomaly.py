"""Dosage validation page."""

import streamlit as st
from core.anomaly.dosage_anomaly_detector import DosageAnomalyDetector


def show():
    """Show dosage anomaly page."""
    st.header("💊 Dosage Validator")
    st.markdown("Validate medication dosages against safety guidelines.")
    
    # Patient context
    with st.expander("Patient Information (optional)"):
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
        
        patient_context = {
            'age': age,
            'weight': weight,
            'renal_impairment': st.checkbox("Renal impairment"),
            'hepatic_impairment': st.checkbox("Hepatic impairment")
        }
    
    # Check current prescription or manual entry
    if st.session_state.current_prescription:
        st.info("Checking current prescription...")
        
        detector = DosageAnomalyDetector()
        
        with st.spinner("Validating..."):
            results = detector.check_prescription(
                st.session_state.current_prescription,
                patient_context
            )
        
        # Display results
        has_issues = any(r.get('has_anomaly') for r in results)
        
        if has_issues:
            st.error("⚠️ Dosage issues detected!")
        else:
            st.success("✅ All dosages appear safe")
        
        for result in results:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.write(f"**{result['medication']}**")
                
                with col2:
                    if result.get('has_anomaly'):
                        severity = result.get('severity', 'warning')
                        if severity == 'danger':
                            st.error(result.get('primary_issue', ''))
                        else:
                            st.warning(result.get('primary_issue', ''))
                        
                        st.info(f"Recommendation: {result.get('recommendation', '')}")
                    else:
                        st.success(result.get('primary_issue', 'OK'))
    else:
        st.info("Parse a prescription first to validate dosages.")