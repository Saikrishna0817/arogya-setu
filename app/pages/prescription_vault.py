"""Prescription history vault page."""

import streamlit as st
import pandas as pd
from core.vault.vault_manager import VaultManager


@st.cache_resource
def get_vault():
    """Get vault manager."""
    return VaultManager()


def show():
    """Show prescription vault page."""
    st.header("🗄️ Prescription History")
    st.markdown("View and search your saved prescriptions.")
    
    vault = get_vault()
    
    # Statistics
    stats = vault.get_statistics()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", stats['total_records'])
    col2.metric("Unique Patients", stats['unique_patients'])
    col3.metric("Last 30 Days", stats['last_30_days'])
    
    # Search
    search_term = st.text_input("Search by patient name")
    
    # List prescriptions
    records = vault.list_prescriptions(
        patient_name=search_term if search_term else None,
        limit=50
    )
    
    if not records:
        st.info("No prescriptions found.")
        return
    
    # Display as table
    df_data = []
    for r in records:
        df_data.append({
            'ID': r.get('id'),
            'Date': r.get('date'),
            'Patient': r.get('patient_name'),
            'Doctor': r.get('doctor_name'),
            'Medications': len(r.get('medications', []))
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)
    
    # View details
    selected_id = st.selectbox(
        "Select prescription to view",
        options=[r['id'] for r in records],
        format_func=lambda x: f"ID: {x}"
    )
    
    if selected_id:
        record = vault.get_prescription(selected_id)
        if record:
            with st.expander("Prescription Details", expanded=True):
                st.write(f"**Patient:** {record.get('patient_name')}")
                st.write(f"**Doctor:** {record.get('doctor_name')}")
                st.write(f"**Date:** {record.get('date')}")
                
                st.subheader("Medications")
                for med in record.get('medications', []):
                    st.write(f"- {med.get('name')} {med.get('strength', '')}")
                
                st.subheader("Explanation")
                st.write(record.get('explanation', 'N/A'))
            
            if st.button("Load into Parser"):
                st.session_state.current_prescription = record
                st.success("Loaded! Go to Prescription Parser to view.")
            
            if st.button("Delete", type="secondary"):
                if vault.delete_prescription(selected_id):
                    st.success("Deleted")
                    st.rerun()