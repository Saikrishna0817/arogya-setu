"""Detect dosage anomalies in prescriptions."""

from typing import List, Dict, Optional
import logging

from core.anomaly.anomaly_rules import AnomalyRules
from core.parsing.prescription_parser import Prescription, Medication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DosageAnomalyDetector:
    """Check prescription for dosage anomalies."""
    
    def __init__(self):
        self.rules = AnomalyRules()
    
    def check_medication(self, med: Medication, 
                        patient_context: Optional[Dict] = None) -> Dict:
        """
        Check single medication for dosage issues.
        
        Args:
            med: Medication to check
            patient_context: Optional age, weight, renal function, etc.
            
        Returns:
            Anomaly report
        """
        if not med.strength_value:
            return {
                'has_anomaly': False,
                'reason': 'no_dose',
                'message': 'Could not parse dose for validation'
            }
        
        # Determine population type
        population = self._determine_population(patient_context)
        
        # Get drug name (prefer generic)
        drug_name = med.generic_name or med.name
        
        # Check against rules
        result = self.rules.check_dose(
            drug_name, 
            med.strength_value,
            med.strength_unit or 'mg',
            population
        )
        
        # Additional heuristics
        anomalies = []
        
        # Check frequency vs dose relationship
        if med.frequency and med.strength_value:
            daily_dose = self._calculate_daily_dose(med)
            if daily_dose:
                daily_check = self.rules.check_dose(
                    drug_name, daily_dose, 
                    med.strength_unit or 'mg', 
                    population
                )
                if not daily_check['is_safe']:
                    anomalies.append(f"Daily dose {daily_dose}{med.strength_unit} concern: {daily_check['message']}")
        
        # Age-specific checks
        if patient_context and 'age' in patient_context:
            age = patient_context['age']
            if age < 12 and not self._is_pediatric_safe(drug_name):
                anomalies.append("Drug may not be pediatric-appropriate")
            elif age > 65:
                elderly_check = self.rules.get_rule(drug_name, 'elderly')
                if elderly_check and med.strength_value > elderly_check.max_dose:
                    anomalies.append("Consider reduced dose for elderly")
        
        return {
            'has_anomaly': not result['is_safe'] or len(anomalies) > 0,
            'severity': result.get('severity', 'unknown'),
            'primary_issue': result.get('message', ''),
            'additional_concerns': anomalies,
            'recommendation': self._get_recommendation(result, med),
            'rule_applied': result.get('has_rule', False)
        }
    
    def check_prescription(self, prescription: Prescription,
                          patient_context: Optional[Dict] = None) -> List[Dict]:
        """Check all medications in prescription."""
        results = []
        
        for med in prescription.medications:
            check = self.check_medication(med, patient_context)
            check['medication'] = med.name
            results.append(check)
        
        return results
    
    def _determine_population(self, context: Optional[Dict]) -> str:
        """Determine population type from context."""
        if not context:
            return 'adult'
        
        age = context.get('age')
        if age:
            if age < 18:
                return 'pediatric'
            elif age > 65:
                return 'elderly'
        
        if context.get('renal_impairment'):
            return 'renal_impairment'
        
        if context.get('hepatic_impairment'):
            return 'hepatic_impairment'
        
        return 'adult'
    
    def _calculate_daily_dose(self, med: Medication) -> Optional[float]:
        """Calculate total daily dose from frequency."""
        if not med.strength_value or not med.frequency:
            return None
        
        freq_multipliers = {
            'OD': 1, '1-0-0': 1, '0-0-1': 1,
            'BD': 2, '1-0-1': 2,
            'TID': 3, '1-1-1': 3,
            'QID': 4,
        }
        
        multiplier = freq_multipliers.get(med.frequency.upper(), 1)
        return med.strength_value * multiplier
    
    def _is_pediatric_safe(self, drug_name: str) -> bool:
        """Check if drug is generally safe for children."""
        # Simplified - would use pediatric database in production
        unsafe_for_children = ['warfarin', 'metformin', 'atenolol']
        return drug_name.lower() not in unsafe_for_children
    
    def _get_recommendation(self, result: Dict, med: Medication) -> str:
        """Generate clinical recommendation."""
        if result['is_safe']:
            return "Dose appears appropriate"
        
        severity = result.get('severity')
        
        if severity == 'danger':
            return f"URGENT: Verify dose with prescriber immediately. Consider {result.get('recommended_max', 'standard dose')} maximum."
        elif severity == 'warning':
            return f"Review dose: May need adjustment to {result.get('recommended_max', 'lower dose')} range."
        else:
            return "Monitor patient response, dose may be suboptimal."