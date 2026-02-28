"""OCR module with Tesseract and preprocessing."""
from core.ocr.ocr_engine import OcrEngine
from core.ocr.image_preprocess import ImagePreprocessor

__all__ = ['OcrEngine', 'ImagePreprocessor']