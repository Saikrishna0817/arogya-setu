"""Audio playback component."""

import streamlit as st
from typing import Optional


def show_audio_player(audio_bytes: Optional[bytes], 
                      caption: str = "Audio Explanation"):
    """Display audio player with download option."""
    if not audio_bytes:
        st.info("No audio available")
        return
    
    st.audio(audio_bytes, format='audio/mp3')
    
    st.download_button(
        label="Download Audio",
        data=audio_bytes,
        file_name="explanation.mp3",
        mime="audio/mp3"
    )