"""Lab report analysis page."""

import streamlit as st
from pathlib import Path
import tempfile

from core.lab.lab_pdf_parser import LabPDFParser
from core.lab.lab_extractor import LabExtractor
from core.lab.lab_explanation_generator import LabExplanationGenerator


def show():
    """Show lab report page."""
    st.header("🧪 Lab Report Analyzer")
    st.markdown("Upload a lab report PDF for analysis and explanation.")
    
    uploaded_file = st.file_uploader(
        "Upload lab report (PDF)",
        type=['pdf']
    )
    
    if uploaded_file:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = Path(tmp.name)
        
        try:
            # Parse PDF
            with st.spinner("Reading PDF..."):
                parser = LabPDFParser()
                parsed = parser.parse(tmp_path)
            
            st.text_area("Extracted Text", parsed['text'][:2000], height=200)
            
            # Extract lab values
            with st.spinner("Analyzing values..."):
                extractor = LabExtractor()
                
                # Try tables first
                items = []
                for table in parsed['tables']:
                    items.extend(extractor.extract_from_table(table))
                
                # Fallback to text
                if not items:
                    items = extractor.extract_from_text(parsed['text'])
            
            if items:
                st.subheader("Extracted Values")
                
                # Display with color coding
                for item in items:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{item.name}**")
                    with col2:
                        if item.flag == 'H':
                            st.error(f"{item.value} {item.unit} ↑")
                        elif item.flag == 'L':
                            st.warning(f"{item.value} {item.unit} ↓")
                        else:
                            st.success(f"{item.value} {item.unit} ✓")
                    with col3:
                        st.caption(f"Ref: {item.ref_low}-{item.ref_high}")
                
                # Generate explanation
                if st.button("Generate Explanation"):
                    with st.spinner("Analyzing..."):
                        generator = LabExplanationGenerator()
                        explanation = generator.generate(items)
                    
                    st.markdown("### Analysis")
                    st.markdown(explanation)
            else:
                st.warning("Could not extract lab values automatically.")
                
        finally:
            tmp_path.unlink(missing_ok=True)