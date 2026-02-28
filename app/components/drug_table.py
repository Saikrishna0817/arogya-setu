"""Medication table display component."""

import streamlit as st
import pandas as pd
from typing import List, Dict


def show_drug_table(medications: List[Dict]):
    """Display medications in a formatted table."""
    if not medications:
        st.info("No medications to display")
        return
    
    # Prepare data
    df_data = []
    for med in medications:
        df_data.append({
            'Medication': med.get('name', 'Unknown'),
            'Generic': med.get('generic_name', '-'),
            'Strength': med.get('strength', '-'),
            'Frequency': med.get('frequency_meaning') or med.get('frequency', '-'),
            'Duration': med.get('duration', '-'),
            'Confidence': f"{med.get('confidence', 0):.0%}"
        })
    
    df = pd.DataFrame(df_data)
    
    # Style the table
    st.dataframe(
        df,
        column_config={
            'Confidence': st.column_config.ProgressColumn(
                'Confidence',
                help="Parsing confidence",
                format="%.0f%%",
                min_value=0,
                max_value=1
            )
        },
        use_container_width=True,
        hide_index=True
    )