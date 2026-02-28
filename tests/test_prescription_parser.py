"""Tests for prescription parser."""

import pytest
from core.parsing.prescription_parser import PrescriptionParser


def test_parse_medication_line():
    """Test medication line parsing."""
    parser = PrescriptionParser()
    
    line = "Paracetamol 500mg 1-0-1 for 5 days"
    med = parser._parse_medication_line(line)
    
    assert med is not None
    assert "Paracetamol" in med.name
    assert med.strength_value == 500.0
    assert med.frequency == "1-0-1"


def test_parse_full_prescription(sample_prescription_text):
    """Test full prescription parsing."""
    parser = PrescriptionParser()
    
    result = parser.parse(sample_prescription_text)
    
    assert len(result.medications) == 2
    assert result.doctor_name == "Ramesh Kumar"
    assert result.patient_name == "Priya Sharma"