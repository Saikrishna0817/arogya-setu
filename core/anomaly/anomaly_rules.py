"""Rules for detecting dosage anomalies."""

import csv
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

from config.paths import Paths


@dataclass
class DosageRule:
    """Single dosage validation rule."""
    drug_name: str
    min_dose: Optional[float]
    max_dose: float
    unit: str
    frequency: str
    population: str = 'adult'
    adjustment_factor: float = 1.0
    notes: str = ''


class AnomalyRules:
    """Manage dosage validation rules from static CSVs."""
    
    def __init__(self):
        self.rules: Dict[str, List[DosageRule]] = {}
        self._load_from_csvs()
        self._load_builtin_fallback()
    
    def _load_from_csvs(self):
        """Load from your dosage reference CSVs."""
        # Load safe dose ranges
        safe_dose_path = Paths.DATA_DIR / 'dosage_reference' / 'safe_dose_ranges.csv'
        if safe_dose_path.exists():
            self._load_safe_doses(safe_dose_path)
        
        # Load pediatric doses
        pediatric_path = Paths.DATA_DIR / 'dosage_reference' / 'pediatric_doses.csv'
        if pediatric_path.exists():
            self._load_pediatric_doses(pediatric_path)
        
        # Load renal adjustments
        renal_path = Paths.DATA_DIR / 'dosage_reference' / 'renal_adjustments.csv'
        if renal_path.exists():
            self._load_renal_adjustments(renal_path)
    
    def _load_safe_doses(self, csv_path: Path):
        """Load safe_dose_ranges.csv."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                drug = row.get('drug_name', '').strip()
                if not drug:
                    continue
                
                if drug not in self.rules:
                    self.rules[drug] = []
                
                self.rules[drug].append(DosageRule(
                    drug_name=drug,
                    min_dose=self._parse_float(row.get('min_single_dose_mg')),
                    max_dose=self._parse_float(row.get('max_single_dose_mg')) or 
                            self._parse_float(row.get('daily_max_mg')) or 9999,
                    unit=row.get('unit', 'mg'),
                    frequency=row.get('standard_frequency', 'OD'),
                    population='adult',
                    notes=row.get('notes', '')
                ))
    
    def _load_pediatric_doses(self, csv_path: Path):
        """Load pediatric_doses.csv."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                drug = row.get('drug_name', '').strip()
                if not drug:
                    continue
                
                self.rules[drug].append(DosageRule(
                    drug_name=drug,
                    min_dose=None,
                    max_dose=self._parse_float(row.get('max_daily_dose')) or 9999,
                    unit=row.get('unit', 'mg'),
                    frequency=row.get('frequency', 'OD'),
                    population='pediatric',
                    adjustment_factor=self._parse_float(row.get('weight_factor')) or 0.5,
                    notes=f"Weight-based: {row.get('mg_per_kg', '')}"
                ))
    
    def _load_renal_adjustments(self, csv_path: Path):
        """Load renal_adjustments.csv."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                drug = row.get('drug_name', '').strip()
                if not drug:
                    continue
                
                self.rules[drug].append(DosageRule(
                    drug_name=drug,
                    min_dose=None,
                    max_dose=self._parse_float(row.get('adjusted_max_dose')) or 9999,
                    unit=row.get('unit', 'mg'),
                    frequency=row.get('frequency', 'OD'),
                    population='renal_impairment',
                    adjustment_factor=self._parse_float(row.get('dose_reduction_factor')) or 0.5,
                    notes=f"CrCl threshold: {row.get('crcl_threshold', 'unknown')}"
                ))
    
    def _load_builtin_fallback(self):
        """Load built-in data as fallback."""
        from config.dosage_limits import DOSAGE_LIMITS
        
        for drug, limits in DOSAGE_LIMITS.items():
            if drug in self.rules:
                continue  # Skip if already loaded from CSV
            
            self.rules[drug] = []
            
            if 'adult_standard_mg' in limits:
                self.rules[drug].append(DosageRule(
                    drug_name=drug,
                    min_dose=limits.get('adult_standard_mg', 0) * 0.25,
                    max_dose=limits['max_daily_mg'],
                    unit=limits.get('unit', 'mg'),
                    frequency=limits.get('frequency', 'OD'),
                    population='adult',
                    source='builtin'
                ))
    
    def get_rule(self, drug_name: str, population: str = 'adult') -> Optional[DosageRule]:
        """Get rule for drug and population."""
        drug_key = drug_name.lower()
        
        if drug_key not in self.rules:
            return None
        
        for rule in self.rules[drug_key]:
            if rule.population == population:
                return rule
        
        # Fallback to adult rule
        for rule in self.rules[drug_key]:
            if rule.population == 'adult':
                return rule
        
        return self.rules[drug_key][0] if self.rules[drug_key] else None
    
    def check_dose(self, drug_name: str, dose_value: float, 
                   unit: str, population: str = 'adult') -> Dict:
        """Check if dose is within safe limits."""
        rule = self.get_rule(drug_name, population)
        
        if not rule:
            return {
                'is_safe': True,
                'severity': 'unknown',
                'message': f"No dosage data for {drug_name}",
                'has_rule': False
            }
        
        # Unit mismatch
        if unit.lower() != rule.unit.lower():
            return {
                'is_safe': True,
                'severity': 'caution',
                'message': f"Unit mismatch: prescribed {unit}, expected {rule.unit}",
                'has_rule': True
            }
        
        # Check limits
        if dose_value > rule.max_dose:
            ratio = dose_value / rule.max_dose
            if ratio > 2.0:
                severity = 'danger'
                message = f"Dose {dose_value}{unit} is {ratio:.1f}x maximum ({rule.max_dose}{unit})!"
            else:
                severity = 'warning'
                message = f"Dose {dose_value}{unit} exceeds recommended {rule.max_dose}{unit}"
            
            return {
                'is_safe': False,
                'severity': severity,
                'message': message,
                'has_rule': True,
                'recommended_max': rule.max_dose,
                'notes': rule.notes
            }
        
        if rule.min_dose and dose_value < rule.min_dose:
            return {
                'is_safe': False,
                'severity': 'info',
                'message': f"Dose {dose_value}{unit} below minimum {rule.min_dose}{unit}",
                'has_rule': True,
                'recommended_min': rule.min_dose
            }
        
        return {
            'is_safe': True,
            'severity': 'ok',
            'message': f"Dose {dose_value}{unit} within safe range",
            'has_rule': True
        }
    
    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        """Safely parse float."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None