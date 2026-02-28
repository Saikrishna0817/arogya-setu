#!/usr/bin/env python
"""End-to-end pipeline validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ocr.ocr_engine import OcrEngine
from core.parsing.prescription_parser import PrescriptionParser
from core.explanation.explanation_generator import ExplanationGenerator


def test_ocr():
    """Test OCR component."""
    print("Testing OCR...")
    engine = OcrEngine(lang='en')
    # Would test with sample image
    print("✓ OCR initialized")


def test_parser():
    """Test parser component."""
    print("Testing Parser...")
    parser = PrescriptionParser()
    
    sample_text = """
    Dr. Smith
    Patient: John Doe
    Date: 01/01/2024
    
    1. Paracetamol 500mg 1-0-1 for 5 days
    2. Amoxicillin 250mg TDS for 7 days
    """
    
    result = parser.parse(sample_text)
    assert len(result.medications) == 2
    print(f"✓ Parser working: found {len(result.medications)} medications")


def test_explainer():
    """Test explanation generator."""
    print("Testing Explanation Generator...")
    generator = ExplanationGenerator(use_llm=False)
    print("✓ Explainer initialized")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Pipeline Validation")
    print("=" * 50)
    
    try:
        test_ocr()
        test_parser()
        test_explainer()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()