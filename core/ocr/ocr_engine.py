"""Tesseract OCR engine with language support and confidence scoring."""

import os
import pytesseract
# Windows Tesseract path configuration
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        os.environ['TESSERACT_CMD'] = tesseract_path
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple,Union
import logging
import json
import re

from config.settings import Settings
from config.languages import LANG_CONFIG
from core.ocr.image_preprocess import ImagePreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure tesseract path if needed
if Settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = Settings.TESSERACT_CMD


class OcrResult:
    """Structured OCR result with metadata."""
    
    def __init__(self, text: str, confidence: float, language: str, 
                 words: List[Dict], raw_data: Dict):
        self.text = text
        self.confidence = confidence
        self.language = language
        self.words = words  # List of {text, conf, bbox}
        self.raw_data = raw_data
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'confidence': self.confidence,
            'language': self.language,
            'word_count': len(self.words),
            'words': self.words[:20]  # Limit for display
        }


class OcrEngine:
    """Tesseract-based OCR with multi-language support."""
    
    def __init__(self, lang: str = 'eng', preprocess: bool = True):
        """
        Initialize OCR engine.
        
        Args:
            lang: Language code ('en', 'hi', 'te', etc.)
            preprocess: Whether to apply image preprocessing
        """
        self.lang_code = lang
        self.tesseract_lang = LANG_CONFIG.get(lang, {}).get('tesseract_lang', 'eng')
        self.preprocessor = ImagePreprocessor() if preprocess else None
        self.use_preprocessing = preprocess
        
        logger.info(f"OCR Engine initialized for language: {self.tesseract_lang}")
    
    def extract(self, image_path: Union[str, Path], 
                return_confidence: bool = True) -> OcrResult:
        """
        Extract text from image with full metadata.
        
        Args:
            image_path: Path to image file
            return_confidence: Whether to include confidence scores
            
        Returns:
            OcrResult with text and metadata
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Preprocess
        if self.use_preprocessing:
            processed = self.preprocessor.preprocess(image_path)
            # Convert to PIL for tesseract
            pil_image = self.preprocessor.enhance_for_display(processed)
        else:
            pil_image = Image.open(image_path)
        
        # OCR configuration
        custom_config = r'--oem 3 --psm 6'  # LSTM engine, assume uniform block
        
        # Get detailed data
        data = pytesseract.image_to_data(
            pil_image, 
            lang=self.tesseract_lang,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Parse results
        words = []
        text_parts = []
        confidences = []
        
        for i, text in enumerate(data['text']):
            conf = int(data['conf'][i])
            if conf > 0 and text.strip():  # Valid word
                word_info = {
                    'text': text,
                    'confidence': conf / 100.0,
                    'bbox': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'w': data['width'][i],
                        'h': data['height'][i]
                    }
                }
                words.append(word_info)
                text_parts.append(text)
                confidences.append(conf)
        
        full_text = ' '.join(text_parts)
        avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
        
        # Post-process text
        full_text = self._post_process(full_text)
        
        logger.info(f"OCR complete: {len(words)} words, confidence: {avg_confidence:.2f}")
        
        return OcrResult(
            text=full_text,
            confidence=avg_confidence,
            language=self.lang_code,
            words=words,
            raw_data=data
        )
    
    def extract_simple(self, image_path: Union[str, Path]) -> str:
        """Quick text extraction without metadata."""
        result = self.extract(image_path, return_confidence=False)
        return result.text
    
    def extract_hocr(self, image_path: Union[str, Path]) -> str:
        """Extract HTML-like hOCR output for structured parsing."""
        pil_image = Image.open(image_path)
        if self.use_preprocessing:
            processed = self.preprocessor.preprocess(image_path)
            pil_image = self.preprocessor.enhance_for_display(processed)
        
        hocr = pytesseract.image_to_pdf_or_hocr(
            pil_image,
            lang=self.tesseract_lang,
            extension='hocr'
        )
        return hocr.decode('utf-8') if isinstance(hocr, bytes) else hocr
    
    def _post_process(self, text: str) -> str:
        """Clean up OCR artifacts common in prescriptions."""
        # Fix common OCR errors
        replacements = {
            '0': 'O',  # Zero to letter O in contexts
            '1': 'I',  # One to I
            '@': 'a',  # Email symbol to a
            '$': 's',  # Dollar to s
            '5': 'S',  # Five to S in some contexts
        }
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Common medical abbreviation fixes
        text = re.sub(r'\b0D\b', 'OD', text)  # Zero-D to OD
        text = re.sub(r'\b8D\b', 'BD', text)  # 8 to B
        text = re.sub(r'\b1D\b', 'OD', text)
        
        return text.strip()
    
    def detect_language(self, image_path: Union[str, Path]) -> str:
        """Attempt to detect script language from image."""
        # Try English first
        result_en = self.extract(image_path)
        
        # If low confidence, try other languages
        if result_en.confidence < 0.5:
            for lang in ['hi', 'te']:
                engine = OcrEngine(lang=lang, preprocess=False)
                result = engine.extract(image_path)
                if result.confidence > result_en.confidence:
                    return lang
        
        return 'en'
    
    def batch_process(self, image_paths: List[Path]) -> List[OcrResult]:
        """Process multiple images."""
        results = []
        for path in image_paths:
            try:
                result = self.extract(path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
                results.append(None)
        return results


class MultiLanguageOcr:
    """Try multiple languages and pick best result."""
    
    def __init__(self):
        self.engines = {
            'en': OcrEngine('en'),
            'hi': OcrEngine('hi'),
            'te': OcrEngine('te')
        }
    
    def extract_best(self, image_path: Union[str, Path]) -> Tuple[str, OcrResult]:
        """Extract using all languages, return best confidence."""
        best_result = None
        best_lang = 'en'
        best_conf = 0.0
        
        for lang, engine in self.engines.items():
            try:
                result = engine.extract(image_path)
                if result.confidence > best_conf:
                    best_conf = result.confidence
                    best_result = result
                    best_lang = lang
            except Exception as e:
                logger.warning(f"{lang} OCR failed: {e}")
        
        if best_result is None:
            raise RuntimeError("All OCR engines failed")
        
        return best_lang, best_result