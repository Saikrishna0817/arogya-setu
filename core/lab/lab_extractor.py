"""Extract structured lab values from PDF content."""

import re
import csv
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from config.paths import Paths


@dataclass
class LabItem:
    """Single lab test result."""
    name: str
    value: float
    unit: str
    reference_range: Optional[str] = None
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    flag: Optional[str] = None  # H, L, or None
    category: Optional[str] = None
    interpretation: Optional[str] = None  # From your CSV


class LabExtractor:
    """Extract lab values using your reference data."""
    
    def __init__(self):
        self.reference_data = self._load_reference_csv()
        self.test_patterns = self._build_patterns()
    
    def _load_reference_csv(self) -> Dict[str, Dict]:
        """Load your lab_reference.csv."""
        ref_path = Paths.DATA_DIR / 'lab_reports' / 'lab_reference.csv'
        
        if not ref_path.exists():
            return self._get_default_reference()
        
        reference = {}
        
        with open(ref_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_name = row.get('test_name', '').strip()
                if not test_name:
                    continue
                
                # Handle multiple name variations
                names = [test_name]
                if 'alternate_names' in row:
                    names.extend(row['alternate_names'].split('|'))
                
                for name in names:
                    name_clean = name.strip().lower()
                    reference[name_clean] = {
                        'test_name': test_name,
                        'loinc_code': row.get('loinc_code', ''),
                        'unit': row.get('unit', ''),
                        'normal_low': self._parse_float(row.get('male_low')) or 
                                     self._parse_float(row.get('normal_low')),
                        'normal_high': self._parse_float(row.get('male_high')) or 
                                      self._parse_float(row.get('normal_high')),
                        'female_low': self._parse_float(row.get('female_low')),
                        'female_high': self._parse_float(row.get('female_high')),
                        'critical_low': self._parse_float(row.get('critical_low')),
                        'critical_high': self._parse_float(row.get('critical_high')),
                        'category': row.get('category', 'General'),
                        'interpretation': row.get('interpretation', '')
                    }
        
        return reference
    
    def _get_default_reference(self) -> Dict[str, Dict]:
        """Fallback reference data."""
        return {
            'hemoglobin': {
                'test_name': 'Hemoglobin',
                'unit': 'g/dL',
                'normal_low': 12.0,
                'normal_high': 16.0,
                'category': 'CBC',
                'interpretation': 'Low: Anaemia, High: Polycythaemia'
            },
            'glucose': {
                'test_name': 'Glucose',
                'unit': 'mg/dL',
                'normal_low': 70,
                'normal_high': 100,
                'category': 'Metabolic',
                'interpretation': 'High: Diabetes, Low: Hypoglycaemia'
            }
        }
    
    def _build_patterns(self) -> Dict[str, str]:
        """Build regex patterns from reference names."""
        patterns = {}
        for name in self.reference_data.keys():
            # Create flexible pattern
            pattern = name.replace(' ', r'\s*')
            patterns[name] = pattern
        return patterns
    
    def extract_from_text(self, text: str, patient_gender: str = 'male') -> List[LabItem]:
        """Extract lab values from text."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            item = self._parse_line(line, patient_gender)
            if item:
                items.append(item)
        
        return items
    
    def _parse_line(self, line: str, patient_gender: str) -> Optional[LabItem]:
        """Parse single line for lab value."""
        line_lower = line.lower()
        
        # Find matching test
        matched_test = None
        for test_name, pattern in self.test_patterns.items():
            if re.search(r'\b' + pattern + r'\b', line_lower):
                matched_test = test_name
                break
        
        if not matched_test:
            return None
        
        ref = self.reference_data[matched_test]
        
        # Extract numeric value
        number_match = re.search(r'(\d+\.?\d*)', line)
        if not number_match:
            return None
        
        value = float(number_match.group(1))
        
        # Determine reference range based on gender
        if patient_gender == 'female' and ref.get('female_low'):
            ref_low = ref['female_low']
            ref_high = ref['female_high']
        else:
            ref_low = ref['normal_low']
            ref_high = ref['normal_high']
        
        # Determine flag
        flag = self._determine_flag(value, ref_low, ref_high, 
                                   ref.get('critical_low'), 
                                   ref.get('critical_high'))
        
        return LabItem(
            name=ref['test_name'],
            value=value,
            unit=ref['unit'],
            ref_low=ref_low,
            ref_high=ref_high,
            flag=flag,
            category=ref['category'],
            interpretation=ref.get('interpretation', '')
        )
    
    def _determine_flag(self, value: float, low: Optional[float], 
                       high: Optional[float],
                       crit_low: Optional[float],
                       crit_high: Optional[float]) -> Optional[str]:
        """Determine H/L/C flag."""
        if crit_low and value < crit_low:
            return 'C'  # Critical low
        if crit_high and value > crit_high:
            return 'C'  # Critical high
        if low and value < low:
            return 'L'
        if high and value > high:
            return 'H'
        return None
    
    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        """Safely parse float."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None