"""Chronic patient management page."""

import streamlit as st
from core.chronic.chronic_patient_manager import ChronicPatientManager
from core.chronic.multi_rx_aggregator import MultiRxAggregator
from core.chronic.conflict_resolver import ConflictResolver


def show():
    """Show chronic patient mode page."""
    st.header("🏥 Chronic Patient Mode")
    st.markdown("Manage multiple prescriptions and long-term medications.")
    
    # Patient selection/management
    manager = ChronicPatientManager()
    
    tab1, tab2 = st.tabs(["Existing Patient", "New Patient"])
    
    with tab1:
        patients = manager.list_patients()
        if patients:
            selected = st.selectbox(
                "Select Patient",
                options=patients,
                format_func=lambda x: f"{x['name']} (ID: {x['id']})"
            )
            
            if selected:
                patient = manager.load_patient(selected['id'])
                show_patient_dashboard(patient)
        else:
            st.info("No patients found. Create a new patient.")
    
    with tab2:
        with st.form("new_patient"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            conditions = st.text_area("Conditions (comma-separated)")
            
            if st.form_submit_button("Create Patient"):
                patient_id = name.lower().replace(' ', '_')
                patient = manager.create_patient(
                    patient_id=patient_id,
                    name=name,
                    age=age,
                    conditions=[c.strip() for c in conditions.split(',') if c.strip()]
                )
                st.success(f"Created patient: {name}")
                st.rerun()


def show_patient_dashboard(patient):
    """Show dashboard for selected patient."""
    st.subheader(f"Patient: {patient.name}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Age", patient.age)
    col2.metric("Conditions", len(patient.conditions))
    col3.metric("Chronic Meds", len(patient.chronic_medications))
    
    # Conditions
    with st.expander("Medical Conditions"):
        for condition in patient.conditions:
            st.write(f"- {condition}")
    
    # Load prescriptions for this patient
    # This would integrate with vault to filter by patient name
    st.subheader("Prescription Analysis")
    
    if st.button("Check for Conflicts"):
        # This would load all prescriptions for patient
        st.info("Conflict checking would analyze all patient prescriptions")