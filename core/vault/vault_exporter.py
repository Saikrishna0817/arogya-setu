"""Export vault data to various formats."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional  # ADD THIS LINE - Optional was missing
from datetime import datetime


class VaultExporter:
    """Export prescription history."""
    
    def __init__(self, vault_manager):
        self.vault = vault_manager
    
    def export_to_csv(self, output_path: Path, 
                      patient_name: Optional[str] = None) -> str:  # Now Optional is defined
        """Export to CSV format."""
        records = self.vault.list_prescriptions(patient_name)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Date', 'Patient', 'Doctor', 'Diagnosis',
                'Medications', 'Created At'
            ])
            
            # Data
            for r in records:
                meds = json.dumps(r.get('medications', []))
                writer.writerow([
                    r.get('id'),
                    r.get('date'),
                    r.get('patient_name'),
                    r.get('doctor_name'),
                    r.get('diagnosis'),
                    meds,
                    r.get('created_at')
                ])
        
        return str(output_path)
    
    def export_to_pdf(self, output_path: Path,
                      prescription_id: int) -> str:
        """Export single prescription to PDF."""
        record = self.vault.get_prescription(prescription_id)
        
        if not record:
            raise ValueError("Prescription not found")
        
        html_content = f"""
        <html>
        <head><title>Prescription {prescription_id}</title></head>
        <body>
            <h1>Prescription Record</h1>
            <p><strong>Patient:</strong> {record.get('patient_name')}</p>
            <p><strong>Doctor:</strong> {record.get('doctor_name')}</p>
            <p><strong>Date:</strong> {record.get('date')}</p>
            <h2>Medications</h2>
            <pre>{json.dumps(record.get('medications', []), indent=2)}</pre>
        </body>
        </html>
        """
        
        html_path = output_path.with_suffix('.html')
        html_path.write_text(html_content, encoding='utf-8')
        
        return str(html_path)
    
    def generate_report(self, patient_name: str) -> Dict:
        """Generate comprehensive patient report."""
        records = self.vault.list_prescriptions(patient_name, limit=100)
        
        all_drugs = set()
        drug_timeline = []
        
        for r in records:
            for med in r.get('medications', []):
                drug_name = med.get('name') or med.get('generic_name')
                if drug_name:
                    all_drugs.add(drug_name)
                    drug_timeline.append({
                        'date': r.get('date'),
                        'drug': drug_name,
                        'strength': med.get('strength'),
                        'duration': med.get('duration')
                    })
        
        return {
            'patient': patient_name,
            'total_visits': len(records),
            'unique_medications': len(all_drugs),
            'medication_list': sorted(list(all_drugs)),
            'timeline': drug_timeline,
            'generated_at': datetime.now().isoformat()
        }