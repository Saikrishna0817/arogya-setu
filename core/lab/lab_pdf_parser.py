"""Parse lab report PDFs."""

import pdfplumber
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabPDFParser:
    """Extract text and tables from lab PDFs."""
    
    def __init__(self):
        pass
    
    def parse(self, pdf_path: Path) -> Dict:
        """
        Parse PDF using multiple methods for best extraction.
        
        Returns:
            Dict with text, tables, and metadata
        """
        result = {
            'text': '',
            'tables': [],
            'metadata': {},
            'pages': 0
        }
        
        # Method 1: pdfplumber (better for tables)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result['pages'] = len(pdf.pages)
                
                all_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        result['tables'].append(table)
                
                result['text'] = '\n'.join(all_text)
                logger.info(f"Extracted {len(result['tables'])} tables with pdfplumber")
        except Exception as e:
            logger.error(f"pdfplumber failed: {e}")
        
        # Method 2: PyMuPDF fallback for better text
        if not result['text']:
            try:
                doc = fitz.open(pdf_path)
                text_parts = []
                
                for page in doc:
                    text_parts.append(page.get_text())
                
                result['text'] = '\n'.join(text_parts)
                result['pages'] = len(doc)
                doc.close()
                logger.info("Used PyMuPDF fallback")
            except Exception as e:
                logger.error(f"PyMuPDF failed: {e}")
        
        # Extract metadata
        result['metadata'] = self._extract_metadata(result['text'])
        
        return result
    
    def _extract_metadata(self, text: str) -> Dict:
        """Extract patient and lab metadata."""
        import re
        
        metadata = {}
        
        # Patient name
        name_match = re.search(r'(?:Patient|Name)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if name_match:
            metadata['patient_name'] = name_match.group(1).strip()
        
        # Date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Lab name
        lab_match = re.search(r'(?:Lab|Laboratory|Centre)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if lab_match:
            metadata['lab_name'] = lab_match.group(1).strip()
        
        return metadata
    
    def extract_tables_as_dataframe(self, pdf_path: Path) -> List:
        """Extract tables as pandas DataFrames."""
        import pandas as pd
        
        dataframes = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        dataframes.append(df)
        
        return dataframes