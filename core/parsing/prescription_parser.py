"""
Prescription parser - extracts structured medication data from OCR text.
Uses hybrid approach: Regex for structured data, heuristics for free text.
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

from core.parsing.drug_name_resolver import DrugNameResolver
from core.parsing.frequency_normalizer import FrequencyNormalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Medication:
    """Structured medication entry."""
    name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    strength: Optional[str] = None  # e.g., "500 mg"
    strength_value: Optional[float] = None
    strength_unit: Optional[str] = None
    frequency: Optional[str] = None  # e.g., "OD", "BD"
    frequency_normalized: Optional[str] = None  # e.g., "once daily"
    duration: Optional[str] = None  # e.g., "5 days", "1 week"
    duration_days: Optional[int] = None
    route: Optional[str] = "oral"  # oral, topical, etc.
    instructions: Optional[str] = None  # Free text
    raw_text: str = ""  # Original OCR line
    confidence: float = 0.0  # Parsing confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'generic_name': self.generic_name,
            'brand_name': self.brand_name,
            'strength': self.strength,
            'frequency': self.frequency,
            'frequency_meaning': self.frequency_normalized,
            'duration': self.duration,
            'duration_days': self.duration_days,
            'instructions': self.instructions,
            'confidence': self.confidence
        }


@dataclass
class Prescription:
    """Complete prescription structure."""
    medications: List[Medication] = field(default_factory=list)
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    date: Optional[str] = None
    diagnosis: Optional[str] = None
    raw_text: str = ""
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_name': self.patient_name,
            'doctor_name': self.doctor_name,
            'date': self.date,
            'diagnosis': self.diagnosis,
            'medications': [m.to_dict() for m in self.medications],
            'medication_count': len(self.medications),
            'parsed_at': self.parsed_at
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class PrescriptionParser:
    """Parse OCR text into structured prescription."""
    
    # Patterns for extraction
    STRENGTH_PATTERN = re.compile(
        r'(\d+(?:\.\d+)?)\s*(mg|mcg|µg|ug|g|ml|iu|units?|%)\b',
        re.IGNORECASE
    )
    
    FREQUENCY_PATTERNS = [
        (r'\b1-0-1\b|\b1\s*-\s*0\s*-\s*1\b', '1-0-1', 'twice daily'),
        (r'\b0-0-1\b|\b0\s*-\s*0\s*-\s*1\b', '0-0-1', 'once at night'),
        (r'\b1-0-0\b|\b1\s*-\s*0\s*-\s*0\b', '1-0-0', 'once in morning'),
        (r'\b0-1-0\b|\b0\s*-\s*1\s*-\s*0\b', '0-1-0', 'once in afternoon'),
        (r'\bOD\b|o\.d\.|once\s+daily', 'OD', 'once daily'),
        (r'\bBD\b|b\.d\.|twice\s+daily|bid', 'BD', 'twice daily'),
        (r'\bTID\b|t\.i\.d\.|thrice\s+daily|tds', 'TID', 'three times daily'),
        (r'\bQID\b|q\.i\.d\.|four\s+times', 'QID', 'four times daily'),
        (r'\bHS\b|h\.s\.|at\s+bedtime', 'HS', 'at bedtime'),
        (r'\bSOS\b|s\.o\.s\.|as\s+needed|prn', 'SOS', 'as needed'),
        (r'\bAC\b|a\.c\.|before\s+(food|meals)', 'AC', 'before meals'),
        (r'\bPC\b|p\.c\.|after\s+(food|meals)', 'PC', 'after meals'),
        (r'\bSTAT\b|stat|immediately', 'STAT', 'immediately'),
        (r'\bOM\b|every\s+morning', 'OM', 'every morning'),
        (r'\bON\b|every\s+night', 'ON', 'every night'),
    ]
    
    DURATION_PATTERNS = [
        (r'for\s+(\d+)\s*days?', 'days'),
        (r'for\s+(\d+)\s*weeks?', 'weeks'),
        (r'for\s+(\d+)\s*months?', 'months'),
        (r'(\d+)\s*days?\s*course', 'days'),
        (r'x\s*(\d+)\s*days?', 'days'),
        (r'×\s*(\d+)\s*days?', 'days'),
    ]
    
    def __init__(self, drug_list_path: Optional[Path] = None):
        self.drug_resolver = DrugNameResolver(drug_list_path)
        self.freq_normalizer = FrequencyNormalizer()
        self.medication_indicators = [
            'tab', 'tablet', 'cap', 'capsule', 'syrup', 'susp', 
            'drops', 'inj', 'injection', 'ointment', 'cream', 
            'mg', 'mcg', 'ml', 'g', '%'
        ]
        logger.info("Prescription parser initialized")
    
    def parse(self, ocr_text: str) -> Prescription:
        """
        Main parsing method.
        
        Args:
            ocr_text: Raw OCR output
            
        Returns:
            Structured Prescription object
        """
        prescription = Prescription(raw_text=ocr_text)
        
        # Extract header info
        prescription = self._extract_header(prescription, ocr_text)
        
        # Split into lines and identify medication entries
        lines = ocr_text.split('\n')
        medications = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Check if line looks like a medication
            if self._is_medication_line(line):
                med = self._parse_medication_line(line)
                if med:
                    medications.append(med)
        
        prescription.medications = medications
        
        # Cross-validation
        prescription = self._validate_prescription(prescription)
        
        logger.info(f"Parsed {len(medications)} medications")
        return prescription
    
    def _is_medication_line(self, line: str) -> bool:
        """Heuristic to identify medication lines."""
        line_lower = line.lower()
        
        # Check for medication indicators
        has_indicator = any(ind in line_lower for ind in self.medication_indicators)
        
        # Check for strength pattern
        has_strength = self.STRENGTH_PATTERN.search(line) is not None
        
        # Check for frequency
        has_frequency = any(re.search(pat[0], line, re.IGNORECASE) 
                          for pat in self.FREQUENCY_PATTERNS)
        
        # Check for numbered list (1., 1), -, •)
        is_list_item = bool(re.match(r'^[\d\-\•\*\■\○\.\s]+', line))
        
        return (has_indicator or has_strength or has_frequency or is_list_item)
    
    def _parse_medication_line(self, line: str) -> Optional[Medication]:
        """Parse single medication line."""
        med = Medication(raw_text=line)
        
        # Extract strength
        strength_match = self.STRENGTH_PATTERN.search(line)
        if strength_match:
            med.strength_value = float(strength_match.group(1))
            med.strength_unit = strength_match.group(2).lower()
            med.strength = f"{med.strength_value} {med.strength_unit}"
        
        # Extract frequency
        for pattern, code, meaning in self.FREQUENCY_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                med.frequency = code
                med.frequency_normalized = meaning
                break
        
        # Extract duration
        for pattern, unit in self.DURATION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                med.duration = f"{value} {unit}"
                # Convert to days
                if unit == 'days':
                    med.duration_days = value
                elif unit == 'weeks':
                    med.duration_days = value * 7
                elif unit == 'months':
                    med.duration_days = value * 30
                break
        
        # Extract drug name (remaining text after removing patterns)
        name_part = self._extract_drug_name(line, med)
        if name_part:
            med.name = name_part
            # Resolve to generic
            resolved = self.drug_resolver.resolve(name_part)
            if resolved:
                med.generic_name = resolved.get('generic')
                med.brand_name = resolved.get('brand')
                med.confidence = resolved.get('confidence', 0.5)
        
        # Extract additional instructions (text in parentheses or after '-')
        instr_match = re.search(r'[\-\(](.+)$', line)
        if instr_match:
            med.instructions = instr_match.group(1).strip(') ')
        
        return med if med.name else None
    
    def _extract_drug_name(self, line: str, med: Medication) -> Optional[str]:
        """Extract drug name by removing structured elements."""
        # Remove strength
        name = self.STRENGTH_PATTERN.sub('', line)
        
        # Remove frequency patterns
        for pattern, _, _ in self.FREQUENCY_PATTERNS:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Remove duration patterns
        for pattern, _ in self.DURATION_PATTERNS:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Remove common prefixes/artifacts
        name = re.sub(r'^[\d\-\•\*\■\○\.\s]+', '', name)
        name = re.sub(r'\b(tab|tablet|cap|capsule|syrup|inj)\b', '', name, flags=re.IGNORECASE)
        
        # Clean up
        name = ' '.join(name.split())
        
        return name if len(name) > 2 else None
    
    def _extract_header(self, prescription: Prescription, text: str) -> Prescription:
        """Extract prescription metadata."""
        # Patient name
        patient_match = re.search(r'(?:Patient|Pt|Name)[\s:]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
        if patient_match:
            prescription.patient_name = patient_match.group(1).strip()
        
        # Doctor name
        doctor_match = re.search(r'(?:Dr|Doctor|Physician)[\s\.:]+([A-Za-z\s\.]+)', text, re.IGNORECASE)
        if doctor_match:
            prescription.doctor_name = doctor_match.group(1).strip()
        
        # Date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                prescription.date = date_match.group(1)
                break
        
        # Diagnosis
        diag_match = re.search(r'(?:Diagnosis|Dx|For)[\s:]+([^\n]+)', text, re.IGNORECASE)
        if diag_match:
            prescription.diagnosis = diag_match.group(1).strip()
        
        return prescription
    
    def _validate_prescription(self, prescription: Prescription) -> Prescription:
        """Cross-validate and flag issues."""
        for med in prescription.medications:
            # Flag if no frequency found
            if not med.frequency:
                med.confidence *= 0.8
            
            # Flag if no duration found
            if not med.duration:
                med.confidence *= 0.9
            
            # Flag if drug name not in database
            if not med.generic_name:
                med.confidence *= 0.7
        
        return prescription
    
    def parse_batch(self, ocr_texts: List[str]) -> List[Prescription]:
        """Parse multiple prescriptions."""
        return [self.parse(text) for text in ocr_texts]