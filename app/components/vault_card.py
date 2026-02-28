"""Prescription history card component."""

import streamlit as st
from typing import Dict


def show_vault_card(record: Dict, on_load=None, on_delete=None):
    """Display prescription card."""
    with st.container():
        st.markdown(f"""
        **{record.get('patient_name', 'Unknown Patient')}**
        - Date: {record.get('date', 'Unknown')}
        - Doctor: {record.get('doctor_name', 'Unknown')}
        - Medications: {len(record.get('medications', []))}
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if on_load and st.button("Load", key=f"load_{record['id']}"):
                on_load(record)
        
        with col2:
            if on_delete and st.button("Delete", key=f"del_{record['id']}"):
                on_delete(record['id'])