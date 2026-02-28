"""Unified dashboard combining prescription, lab, and safety features."""

import streamlit as st
from datetime import datetime

from core.ocr.ocr_engine import OcrEngine
from core.parsing.prescription_parser import PrescriptionParser
from core.explanation.explanation_generator import ExplanationGenerator
from core.interaction.interaction_checker import InteractionChecker
from core.anomaly.dosage_anomaly_detector import DosageAnomalyDetector
from core.schedule.schedule_generator import ScheduleGenerator
from core.vault.vault_manager import VaultManager


def show():
    """Show unified dashboard."""
    st.header("📊 Unified Health Dashboard")
    st.markdown("Complete overview of prescriptions, interactions, and schedules.")
    
    # Initialize components
    vault = VaultManager()
    
    # Quick stats
    stats = vault.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Prescriptions", stats['total_records'])
    col2.metric("Patients", stats['unique_patients'])
    col3.metric("This Month", stats['last_30_days'])
    col4.metric("Encrypted", "Yes" if stats['encrypted'] else "No")
    
    # Recent activity
    st.subheader("Recent Prescriptions")
    recent = vault.list_prescriptions(limit=5)
    
    for rx in recent:
        with st.expander(f"{rx.get('patient_name', 'Unknown')} - {rx.get('date', 'No date')}"):
            st.write(f"Doctor: {rx.get('doctor_name', 'Unknown')}")
            st.write(f"Medications: {len(rx.get('medications', []))}")
            if st.button("Load", key=f"load_{rx['id']}"):
                st.session_state.current_prescription = rx
                st.success("Loaded to parser!")
    
    # Safety overview
    if st.session_state.current_prescription:
        st.subheader("Current Prescription Safety")
        
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("**Interactions**")
            checker = InteractionChecker()
            result = checker.check_prescription([
                {'name': m.get('name'), 'generic_name': m.get('generic_name')}
                for m in st.session_state.current_prescription.get('medications', [])
            ])
            
            if result['interactions_found']:
                st.error(f"⚠️ {result['total_interactions']} found")
            else:
                st.success("✅ None")
        
        with cols[1]:
            st.markdown("**Dosage Check**")
            detector = DosageAnomalyDetector()
            checks = detector.check_prescription(st.session_state.current_prescription)
            issues = [c for c in checks if c.get('has_anomaly')]
            
            if issues:
                st.warning(f"⚡ {len(issues)} issues")
            else:
                st.success("✅ OK")
        
        with cols[2]:
            st.markdown("**Schedule**")
            generator = ScheduleGenerator()
            schedule = generator.generate(st.session_state.current_prescription)
            total_meds = sum(len(v) for v in schedule.values())
            st.info(f"📅 {total_meds} slots")