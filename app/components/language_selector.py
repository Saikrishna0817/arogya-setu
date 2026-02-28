"""Language and voice selection component."""

import streamlit as st
from config.languages import LANG_CONFIG


def language_selector(key_prefix: str = ""):
    """Show language and voice selectors."""
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Language",
            options=list(LANG_CONFIG.keys()),
            format_func=lambda x: LANG_CONFIG[x]['name'],
            key=f"{key_prefix}_lang"
        )
    
    with col2:
        voices = LANG_CONFIG[language].get('voices', [])
        voice = st.selectbox(
            "Voice",
            options=[v['id'] for v in voices],
            format_func=lambda x: next(
                (v['name'] for v in voices if v['id'] == x), x
            ),
            key=f"{key_prefix}_voice"
        )
    
    return language, voice