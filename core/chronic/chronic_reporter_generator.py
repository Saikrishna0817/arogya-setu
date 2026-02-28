"""Generate comprehensive reports for chronic patients."""

from typing import List, Dict
from datetime import datetime

from core.chronic.chronic_patient_manager import PatientProfile
from core.chronic.multi_rx_aggregator import MultiRxAggregator
from core.chronic.conflict_resolver import ConflictResolver
from core.parsing.prescription_parser import Prescription


class ChronicReportGenerator:
    """Generate patient summary reports."""
    
    def __init__(self):
        self.aggregator = MultiRxAggregator()
        self.resolver = ConflictResolver()
    
    def generate(self, patient: PatientProfile, 
                 prescriptions: List[Prescription]) -> Dict:
        """
        Generate comprehensive chronic patient report.
        
        Args:
            patient: Patient profile
            prescriptions: All historical prescriptions
            
        Returns:
            Comprehensive report dict
        """
        # Aggregate prescriptions
        for rx in prescriptions:
            self.aggregator.add_prescription(rx, str(id(rx)))
        
        # Check conflicts
        conflicts = self.resolver.resolve_all(prescriptions)
        
        # Build report
        report = {
            'generated_at': datetime.now().isoformat(),
            'patient': {
                'name': patient.name,
                'age': patient.age,
                'conditions': patient.conditions,
                'allergies': patient.allergies
            },
            'medication_summary': self.aggregator.generate_summary(),
            'conflicts': conflicts,
            'adherence_assessment': self._assess_adherence(prescriptions),
            'monitoring_recommendations': self._get_monitoring_recs(patient)
        }
        
        return report
    
    def _assess_adherence(self, prescriptions: List[Prescription]) -> Dict:
        """Simple adherence assessment based on refill patterns."""
        # This would analyze dates to estimate adherence
        # Simplified version
        return {
            'estimated_adherence': 'unknown',
            'gap_days': [],
            'recommendation': 'Regular follow-up recommended'
        }
    
    def _get_monitoring_recs(self, patient: PatientProfile) -> List[str]:
        """Generate monitoring recommendations."""
        recs = []
        
        for condition in patient.conditions:
            if 'diabetes' in condition.lower():
                recs.append("Monitor HbA1c every 3 months")
                recs.append("Annual eye examination")
            elif 'hypertension' in condition.lower():
                recs.append("Monthly BP monitoring")
                recs.append("Annual kidney function tests")
            elif 'heart' in condition.lower():
                recs.append("Regular lipid panel monitoring")
        
        return recs
    
    def to_html(self, report: Dict) -> str:
        """Convert report to HTML."""
        html = f"""
        <html>
        <head>
            <title>Chronic Care Report - {report['patient']['name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .alert {{ background: #fff3cd; padding: 10px; }}
                .danger {{ background: #f8d7da; }}
            </style>
        </head>
        <body>
            <h1>Chronic Care Summary Report</h1>
            <p>Generated: {report['generated_at']}</p>
            
            <div class="section">
                <h2>Patient Information</h2>
                <p><strong>Name:</strong> {report['patient']['name']}</p>
                <p><strong>Age:</strong> {report['patient']['age']}</p>
                <p><strong>Conditions:</strong> {', '.join(report['patient']['conditions'])}</p>
            </div>
            
            <div class="section">
                <h2>Active Medications</h2>
                <ul>
        """
        
        for med in report['medication_summary'].get('current_medications', []):
            html += f"<li>{med['drug']} - {med['current_prescription']['strength']}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html