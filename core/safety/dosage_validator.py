"""Validate dosages against safety databases."""

from typing import Dict, Optional, List
from dataclasses import dataclass

from config.dosage_limits import DOSAGE_LIMITS, BRAND_TO_GENERIC


@dataclass
class DosageValidationResult:
    """Result of dosage validation."""
    is_safe: bool
    severity: str  # 'ok', 'caution', 'warning', 'danger'
    message: str
    recommended_range: Optional[tuple]
    clinical_notes: str


class DosageValidator:
    """Comprehensive dosage validation."""
    
    def __init__(self):
        self.limits = DOSAGE_LIMITS
        self.brand_map = BRAND_TO_GENERIC
    
    def validate(self, drug_name: str, dose: float, unit: str,
                 frequency: str = 'OD',
                 patient_age: Optional[int] = None,
                 patient_weight: Optional[float] = None) -> DosageValidationResult:
        """
        Validate single dose.
        
        Args:
            drug_name: Generic or brand name
            dose: Prescribed dose amount
            unit: mg, mcg, g, etc.
            frequency: OD, BD, etc.
            patient_age: Years
            patient_weight: kg
            
        Returns:
            DosageValidationResult
        """
        # Normalize drug name
        generic = self._get_generic_name(drug_name)
        
        if generic not in self.limits:
            return DosageValidationResult(
                is_safe=True,  # Unknown drug, can't validate
                severity='unknown',
                message=f"No dosage data for {drug_name}",
                recommended_range=None,
                clinical_notes="Consult specialist for dosing"
            )
        
        limits = self.limits[generic]
        
        # Calculate daily dose
        daily_dose = self._calculate_daily_dose(dose, frequency)
        max_daily = limits.get('max_daily_mg', float('inf'))
        
        # Check unit
        expected_unit = limits.get('unit', 'mg')
        if unit.lower() != expected_unit.lower():
            return DosageValidationResult(
                is_safe=True,
                severity='caution',
                message=f"Unit mismatch: prescribed {unit}, expected {expected_unit}",
                recommended_range=None,
                clinical_notes="Verify unit conversion"
            )
        
        # Age adjustments
        if patient_age:
            adjusted_max = self._adjust_for_age(generic, patient_age, max_daily)
        else:
            adjusted_max = max_daily
        
        # Validate
        if daily_dose > adjusted_max * 1.5:
            return DosageValidationResult(
                is_safe=False,
                severity='danger',
                message=f"Dose {daily_dose}{unit}/day exceeds maximum {adjusted_max}{unit}",
                recommended_range=(limits.get('adult_standard_mg', 0), adjusted_max),
                clinical_notes="Overdose risk - verify with prescriber immediately"
            )
        elif daily_dose > adjusted_max:
            return DosageValidationResult(
                is_safe=False,
                severity='warning',
                message=f"Dose {daily_dose}{unit}/day above recommended {adjusted_max}{unit}",
                recommended_range=(limits.get('adult_standard_mg', 0), adjusted_max),
                clinical_notes="High dose - monitor for adverse effects"
            )
        elif daily_dose < limits.get('adult_standard_mg', 0) * 0.25:
            return DosageValidationResult(
                is_safe=True,
                severity='caution',
                message=f"Dose {daily_dose}{unit}/day is subtherapeutic",
                recommended_range=(limits.get('adult_standard_mg', 0) * 0.5, adjusted_max),
                clinical_notes="May be insufficient for therapeutic effect"
            )
        
        return DosageValidationResult(
            is_safe=True,
            severity='ok',
            message=f"Dose {daily_dose}{unit}/day is within safe range",
            recommended_range=(limits.get('adult_standard_mg', 0) * 0.5, adjusted_max),
            clinical_notes="Standard dosing"
        )
    
    def _get_generic_name(self, drug_name: str) -> str:
        """Convert brand to generic name."""
        name_lower = drug_name.lower()
        
        # Direct match
        if name_lower in self.limits:
            return name_lower
        
        # Brand name match
        for brand, generic in self.brand_map.items():
            if brand.lower() in name_lower:
                return generic.lower()
        
        # Partial match
        for generic in self.limits.keys():
            if generic.lower() in name_lower:
                return generic.lower()
        
        return drug_name
    
    def _calculate_daily_dose(self, dose: float, frequency: str) -> float:
        """Calculate total daily dose."""
        multipliers = {
            'od': 1, '1-0-0': 1, '0-0-1': 1,
            'bd': 2, '1-0-1': 2,
            'tds': 3, 'tid': 3, '1-1-1': 3,
            'qid': 4
        }
        
        multiplier = multipliers.get(frequency.lower(), 1)
        return dose * multiplier
    
    def _adjust_for_age(self, drug: str, age: int, standard_max: float) -> float:
        """Adjust max dose for age."""
        if age < 12:
            # Pediatric - weight-based, rough estimate
            return standard_max * 0.3
        elif age > 65:
            # Elderly
            limits = self.limits.get(drug, {})
            adjustments = limits.get('population_adjustments', {})
            factor = adjustments.get('elderly', 0.75)
            return standard_max * factor
        
        return standard_max
    
    def validate_prescription(self, medications: List[Dict],
                             patient_context: Optional[Dict] = None) -> List[DosageValidationResult]:
        """Validate all medications in prescription."""
        results = []
        
        context = patient_context or {}
        
        for med in medications:
            result = self.validate(
                drug_name=med.get('name') or med.get('generic_name', ''),
                dose=med.get('strength_value', 0),
                unit=med.get('strength_unit', 'mg'),
                frequency=med.get('frequency', 'OD'),
                patient_age=context.get('age'),
                patient_weight=context.get('weight')
            )
            results.append(result)
        
        return results