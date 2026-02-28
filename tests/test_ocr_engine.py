"""Tests for OCR engine."""

import pytest
from core.ocr.ocr_engine import OcrEngine


def test_ocr_engine_init():
    """Test OCR engine initialization."""
    engine = OcrEngine(lang='en')
    assert engine.lang_code == 'en'


def test_ocr_post_process():
    """Test text post-processing."""
    engine = OcrEngine(lang='en')
    
    text = "Take 0D and 8D daily"
    result = engine._post_process(text)
    
    assert "OD" in result
    assert "BD" in result