"""Aggregate multiple prescriptions for chronic patients."""

from typing import List, Dict, Set
from collections import defaultdict

from core.parsing.prescription_parser import Prescription


class MultiRxAggregator:
    """Combine multiple prescriptions into unified view."""
    
    def __init__(self):
        self.medications = defaultdict(list)  # drug_name -> list of prescriptions
        self.timeline = []
    
    def add_prescription(self, prescription: Prescription, 
                        prescription_id: str):
        """Add prescription to aggregation."""
        for med in prescription.medications:
            key = med.generic_name or med.name
            
            self.medications[key].append({
                'prescription_id': prescription_id,
                'date': prescription.date,
                'strength': med.strength,
                'frequency': med.frequency,
                'duration': med.duration,
                'raw_name': med.name
            })
        
        self.timeline.append({
            'id': prescription_id,
            'date': prescription.date,
            'doctor': prescription.doctor_name,
            'medication_count': len(prescription.medications)
        })
    
    def get_medication_history(self, drug_name: str) -> List[Dict]:
        """Get all prescriptions for specific drug."""
        return self.medications.get(drug_name, [])
    
    def identify_changes(self) -> List[Dict]:
        """Identify dosage changes over time."""
        changes = []
        
        for drug, history in self.medications.items():
            if len(history) < 2:
                continue
            
            # Sort by date
            sorted_history = sorted(history, key=lambda x: x.get('date') or '')
            
            for i in range(1, len(sorted_history)):
                prev = sorted_history[i-1]
                curr = sorted_history[i]
                
                # Check for changes
                if prev['strength'] != curr['strength']:
                    changes.append({
                        'drug': drug,
                        'type': 'strength_change',
                        'from': prev['strength'],
                        'to': curr['strength'],
                        'date': curr['date'],
                        'prescription_id': curr['prescription_id']
                    })
                
                if prev['frequency'] != curr['frequency']:
                    changes.append({
                        'drug': drug,
                        'type': 'frequency_change',
                        'from': prev['frequency'],
                        'to': curr['frequency'],
                        'date': curr['date'],
                        'prescription_id': curr['prescription_id']
                    })
        
        return changes
    
    def get_current_medications(self) -> List[Dict]:
        """Get latest prescription for each medication."""
        current = []
        
        for drug, history in self.medications.items():
            if not history:
                continue
            
            # Get most recent
            latest = max(history, key=lambda x: x.get('date') or '')
            current.append({
                'drug': drug,
                'current_prescription': latest,
                'previous_count': len(history) - 1
            })
        
        return current
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive summary."""
        return {
            'total_prescriptions': len(self.timeline),
            'unique_medications': len(self.medications),
            'medication_history': dict(self.medications),
            'timeline': sorted(self.timeline, key=lambda x: x.get('date') or ''),
            'changes': self.identify_changes(),
            'current_medications': self.get_current_medications()
        }