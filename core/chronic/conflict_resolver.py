"""Resolve conflicts across multiple prescriptions."""

from typing import List, Dict, Set, Tuple
from collections import defaultdict

from core.parsing.prescription_parser import Prescription, Medication
from core.parsing.drug_name_resolver import DrugNameResolver
from core.interaction.interaction_checker import InteractionChecker


class ConflictResolver:
    """Detect and resolve prescription conflicts."""
    
    def __init__(self):
        self.resolver = DrugNameResolver()
        self.interaction_checker = InteractionChecker()
    
    def find_duplicates(self, prescriptions: List[Prescription]) -> List[Dict]:
        """Find duplicate medications across prescriptions."""
        # Normalize all drugs
        drug_map = defaultdict(list)  # generic_name -> list of (rx_id, med)
        
        for rx in prescriptions:
            for med in rx.medications:
                generic = self.resolver.resolve(med.name).get('generic') or med.name
                drug_map[generic.lower()].append({
                    'prescription': rx,
                    'medication': med,
                    'date': rx.date
                })
        
        # Find duplicates
        duplicates = []
        for generic, occurrences in drug_map.items():
            if len(occurrences) > 1:
                # Check if truly duplicate (same strength, frequency)
                by_regimen = defaultdict(list)
                for occ in occurrences:
                    key = (occ['medication'].strength, occ['medication'].frequency)
                    by_regimen[key].append(occ)
                
                # Report different regimens as conflicts
                if len(by_regimen) > 1:
                    duplicates.append({
                        'drug': generic,
                        'type': 'different_regimens',
                        'regimens': [
                            {
                                'strength': k[0],
                                'frequency': k[1],
                                'occurrences': v
                            }
                            for k, v in by_regimen.items()
                        ]
                    })
                else:
                    duplicates.append({
                        'drug': generic,
                        'type': 'exact_duplicate',
                        'occurrences': occurrences
                    })
        
        return duplicates
    
    def find_temporal_conflicts(self, prescriptions: List[Prescription]) -> List[Dict]:
        """Find timing conflicts (same drug, overlapping dates)."""
        conflicts = []
        
        # Group by drug
        drug_timeline = defaultdict(list)
        
        for rx in prescriptions:
            for med in rx.medications:
                generic = self.resolver.resolve(med.name).get('generic') or med.name
                drug_timeline[generic.lower()].append({
                    'prescription_date': rx.date,
                    'duration_days': med.duration_days or 30,  # Default assumption
                    'medication': med
                })
        
        # Check for overlaps
        for drug, timeline in drug_timeline.items():
            if len(timeline) < 2:
                continue
            
            # Sort by date
            sorted_timeline = sorted(timeline, key=lambda x: x['prescription_date'] or '')
            
            for i in range(1, len(sorted_timeline)):
                prev = sorted_timeline[i-1]
                curr = sorted_timeline[i]
                
                # Simple date comparison (would need proper date parsing)
                if prev['prescription_date'] == curr['prescription_date']:
                    conflicts.append({
                        'drug': drug,
                        'type': 'same_date',
                        'prescriptions': [prev, curr]
                    })
        
        return conflicts
    
    def find_interactions(self, prescriptions: List[Prescription]) -> List[Dict]:
        """Find drug interactions across all prescriptions."""
        # Collect all medications
        all_meds = []
        for rx in prescriptions:
            all_meds.extend(rx.medications)
        
        # Check interactions
        return self.interaction_checker.check_prescription([
            {'name': m.name, 'generic_name': m.generic_name} 
            for m in all_meds
        ])
    
    def resolve_all(self, prescriptions: List[Prescription]) -> Dict:
        """Run all conflict detection."""
        return {
            'duplicates': self.find_duplicates(prescriptions),
            'temporal_conflicts': self.find_temporal_conflicts(prescriptions),
            'interactions': self.find_interactions(prescriptions),
            'recommendations': self._generate_recommendations(
                prescriptions
            )
        }
    
    def _generate_recommendations(self, prescriptions: List[Prescription]) -> List[str]:
        """Generate resolution recommendations."""
        recs = []
        
        # This would provide specific clinical recommendations
        recs.append("Review duplicate medications for necessity")
        recs.append("Verify dosing consistency across prescriptions")
        recs.append("Check for drug-drug interactions")
        
        return recs