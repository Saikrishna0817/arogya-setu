"""Unified anomaly detection for prescriptions."""

from typing import Dict, List, Optional
from dataclasses import dataclass

from core.anomaly.dosage_anomaly_detector import DosageAnomalyDetector
from core.interaction.interaction_checker import InteractionChecker


@dataclass
class AnomalyReport:
    """Complete anomaly report."""
    prescription_safe: bool
    dosage_issues: List[Dict]
    interaction_issues: List[Dict]
    recommendations: List[str]
    severity_score: int  # 0-10


class AnomalyDetector:
    """Detect all types of anomalies in prescriptions."""
    
    def __init__(self):
        self.dosage_checker = DosageAnomalyDetector()
        self.interaction_checker = InteractionChecker()
    
    def check(self, prescription, patient_context: Optional[Dict] = None) -> AnomalyReport:
        """
        Comprehensive anomaly check.
        
        Args:
            prescription: Parsed prescription
            patient_context: Patient age, weight, conditions
            
        Returns:
            AnomalyReport with all findings
        """
        # Check dosages
        dosage_results = self.dosage_checker.check_prescription(
            prescription, patient_context
        )
        dosage_issues = [r for r in dosage_results if r.get('has_anomaly')]
        
        # Check interactions
        med_dicts = [
            {'name': m.name, 'generic_name': m.generic_name}
            for m in prescription.medications
        ]
        interaction_result = self.interaction_checker.check_prescription(med_dicts)
        interaction_issues = interaction_result.get('interactions', [])
        
        # Calculate severity
        severity = 0
        for issue in dosage_issues:
            if issue.get('severity') == 'danger':
                severity += 3
            elif issue.get('severity') == 'warning':
                severity += 2
            else:
                severity += 1
        
        for inter in interaction_issues:
            sev = inter.get('severity', '').lower()
            if sev == 'contraindicated':
                severity += 5
            elif sev == 'major':
                severity += 3
            elif sev == 'moderate':
                severity += 2
            else:
                severity += 1
        
        # Generate recommendations
        recommendations = []
        if dosage_issues:
            recommendations.append("Review flagged dosages with prescriber")
        if interaction_issues:
            recommendations.append("Check drug interactions before dispensing")
        if not recommendations:
            recommendations.append("No immediate concerns identified")
        
        return AnomalyReport(
            prescription_safe=(len(dosage_issues) == 0 and len(interaction_issues) == 0),
            dosage_issues=dosage_issues,
            interaction_issues=interaction_issues,
            recommendations=recommendations,
            severity_score=min(severity, 10)
        )
    
    def quick_check(self, prescription) -> Dict:
        """Quick safety check with simple output."""
        report = self.check(prescription)
        
        return {
            'safe': report.prescription_safe,
            'severity': report.severity_score,
            'issues_count': len(report.dosage_issues) + len(report.interaction_issues),
            'can_proceed': report.severity_score < 5
        }