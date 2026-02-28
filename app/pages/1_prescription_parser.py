"""Main prescription parsing page."""

import streamlit as st
from PIL import Image
import tempfile
from pathlib import Path

from core.ocr.ocr_engine import OcrEngine
from core.parsing.prescription_parser import PrescriptionParser
from core.explanation.explanation_generator import ExplanationGenerator
from core.explanation.translator import Translator
from core.explanation.tts_engine import TTSEngine
from core.vault.vault_manager import VaultManager


@st.cache_resource
def get_ocr_engine():
    """Lazy load OCR engine."""
    return OcrEngine(lang='en')

@st.cache_resource
def get_parser():
    """Lazy load parser."""
    return PrescriptionParser()

@st.cache_resource
def get_explainer():
    """Lazy load explanation generator."""
    return ExplanationGenerator(use_llm=True)

@st.cache_resource
def get_translator():
    """Lazy load translator."""
    return Translator(use_local=False)

@st.cache_resource
def get_tts():
    """Lazy load TTS."""
    return TTSEngine(use_cloud=False)

@st.cache_resource
def get_vault():
    """Lazy load vault."""
    return VaultManager()


def show():
    """Show prescription parser page."""
    st.header("📄 Prescription Parser")
    st.markdown("Upload a prescription image to extract and explain medications.")
    
    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        target_lang = st.selectbox(
            "Explanation Language",
            options=['en', 'hi', 'te'],
            format_func=lambda x: {'en': 'English', 'hi': 'Hindi', 'te': 'Telugu'}[x]
        )
    
    with col2:
        voice = st.selectbox(
            "Voice",
            options=['male', 'female']
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload prescription image",
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Prescription", use_column_width=True)
        
        # Process button
        if st.button("🔍 Analyze Prescription", type="primary"):
            with st.spinner("Processing..."):
                process_prescription(image, target_lang, voice)


def process_prescription(image, target_lang, voice):
    """Process prescription through pipeline."""
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        image.save(tmp.name)
        tmp_path = Path(tmp.name)
    
    try:
        # Step 1: OCR
        st.subheader("Step 1: Text Extraction")
        ocr_engine = get_ocr_engine()
        
        with st.spinner("Reading prescription..."):
            ocr_result = ocr_engine.extract(tmp_path)
        
        st.text_area("Extracted Text", ocr_result.text, height=150)
        st.info(f"OCR Confidence: {ocr_result.confidence:.1%}")
        
        # Step 2: Parse
        st.subheader("Step 2: Medication Parsing")
        parser = get_parser()
        
        with st.spinner("Parsing medications..."):
            prescription = parser.parse(ocr_result.text)
        
        if not prescription.medications:
            st.warning("No medications found. Please check image quality.")
            return
        
        # Display parsed medications
        meds_data = [m.to_dict() for m in prescription.medications]
        st.dataframe(meds_data, use_container_width=True)
        
        # Step 3: Generate Explanation
        st.subheader("Step 3: Explanation")
        explainer = get_explainer()
        
        with st.spinner("Generating explanation..."):
            explanation = explainer.generate(prescription, style='simple')
            st.session_state.current_explanation = explanation
            st.session_state.current_prescription = prescription
        
        st.markdown("### English Explanation")
        st.markdown(explanation)
        
        # Step 4: Translate
        if target_lang != 'en':
            st.subheader(f"Step 4: Translation ({target_lang})")
            translator = get_translator()
            
            with st.spinner("Translating..."):
                translated = translator.translate_prescription_explanation(
                    explanation, target_lang
                )
            
            st.markdown(f"### Translated Explanation")
            st.markdown(translated)
            text_to_speak = translated
        else:
            text_to_speak = explanation
        
        # Step 5: Text to Speech
        st.subheader("Step 5: Audio Output")
        tts = get_tts()
        
        with st.spinner("Generating audio..."):
            audio_bytes = tts.synthesize(text_to_speak, target_lang, voice)
            st.session_state.current_audio = audio_bytes
        
        st.audio(audio_bytes, format='audio/mp3')
        
        # Save to vault
        if st.button("💾 Save to History"):
            vault = get_vault()
            record_id = vault.save_prescription(
                prescription.to_dict(),
                explanation,
                ocr_result.text
            )
            st.success(f"Saved to history (ID: {record_id})")
        
    finally:
        # Cleanup
        tmp_path.unlink(missing_ok=True)