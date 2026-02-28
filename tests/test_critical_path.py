"""Critical path end-to-end tests."""

import pytest
import tempfile
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import platform

from core.ocr.ocr_engine import OcrEngine
from core.parsing.prescription_parser import PrescriptionParser
from core.explanation.explanation_generator import ExplanationGenerator
from core.interaction.interaction_checker import InteractionChecker
from core.anomaly.dosage_anomaly_detector import DosageAnomalyDetector


class TestCriticalPath:
    """Test complete prescription processing pipeline."""

    @pytest.fixture
    def sample_prescription_image(self):
        """Create test prescription image."""
        img = Image.new('RGB', (1000, 700), color='white')
        draw = ImageDraw.Draw(img)

        text = """
Dr. Test Doctor
Patient: John Doe
Date: 01/01/2024

1. Paracetamol 500mg 1-0-1 for 5 days
2. Amoxicillin 250mg TDS for 7 days
"""

        # Cross-platform font handling
        font = None
        try:
            if platform.system() == "Windows":
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
            else:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
                )
        except:
            font = ImageFont.load_default()

        y = 60
        for line in text.strip().split("\n"):
            draw.text((60, y), line.strip(), fill="black", font=font)
            y += 40

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name, dpi=(300, 300))  # High DPI improves OCR
            return Path(f.name)

    def test_ocr_to_explanation_pipeline(self, sample_prescription_image):
        """Test full pipeline from image to explanation."""
        ocr = OcrEngine(lang="en")
        ocr_result = ocr.extract(sample_prescription_image)

        assert ocr_result.text is not None
        assert len(ocr_result.text) > 0
        assert "paracetamol" in ocr_result.text.lower()

        parser = PrescriptionParser()
        prescription = parser.parse(ocr_result.text)

        assert len(prescription.medications) >= 2
        med_names = [m.name.lower() for m in prescription.medications]
        assert any("paracetamol" in n for n in med_names)

        checker = InteractionChecker()
        med_dicts = [
            {"name": m.name, "generic_name": m.generic_name}
            for m in prescription.medications
        ]
        interaction_result = checker.check_prescription(med_dicts)

        assert "interactions_found" in interaction_result

        detector = DosageAnomalyDetector()
        dosage_results = detector.check_prescription(prescription)

        assert len(dosage_results) == len(prescription.medications)

        explainer = ExplanationGenerator(use_llm=False)
        explanation = explainer.generate(prescription)

        assert len(explanation) > 0
        assert "paracetamol" in explanation.lower() or "medication" in explanation.lower()

    def test_safety_checks(self):
        from core.safety.hallucination_guard import HallucinationGuard

        guard = HallucinationGuard()

        safe_text = "Take your medications as prescribed. Consult your doctor for questions."
        result = guard.check(safe_text)
        assert result["safe"] is True

        unsafe_text = "Stop taking your medications immediately and double the dose."
        result = guard.check(unsafe_text)
        assert result["safe"] is False
        assert len(result["violations"]) > 0

    def test_encryption(self):
        from core.vault.encrypted_storage import EncryptedStorage

        storage = EncryptedStorage()

        test_data = {"patient": "Test", "medication": "Aspirin 100mg"}

        encrypted = storage.encrypt_dict(test_data)
        assert encrypted != json.dumps(test_data).encode()

        decrypted = storage.decrypt_dict(encrypted)
        assert decrypted == test_data


def test_imports():
    import core.ocr.ocr_engine
    import core.parsing.prescription_parser
    import core.explanation.explanation_generator
    import core.interaction.interaction_checker
    import core.anomaly.dosage_anomaly_detector
    import core.vault.vault_manager

    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])