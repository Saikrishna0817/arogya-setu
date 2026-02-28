"""Build optimized medication schedules with constraints."""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.parsing.prescription_parser import Prescription, Medication
from core.parsing.frequency_normalizer import FrequencyNormalizer


@dataclass
class TimeSlot:
    """Scheduled medication time."""
    time: str  # HH:MM format
    medications: List[Dict]
    food_required: bool
    food_forbidden: bool


class ScheduleBuilder:
    """Build optimized daily schedules."""
    
    # Standard timing recommendations
    TIMING_GUIDELINES = {
        'morning': {'start': '07:00', 'end': '09:00', 'with_food': True},
        'afternoon': {'start': '13:00', 'end': '14:00', 'with_food': True},
        'evening': {'start': '18:00', 'end': '20:00', 'with_food': True},
        'night': {'start': '21:00', 'end': '22:00', 'with_food': False},
    }
    
    def __init__(self):
        self.freq_norm = FrequencyNormalizer()
        self.constraints = []
    
    def build_schedule(self, prescription: Prescription,
                      preferences: Dict = None) -> Dict[str, TimeSlot]:
        """
        Build optimized schedule.
        
        Args:
            prescription: Parsed prescription
            preferences: User timing preferences
            
        Returns:
            Dict of slot_name -> TimeSlot
        """
        schedule = {
            'morning': TimeSlot('08:00', [], False, False),
            'afternoon': TimeSlot('13:00', [], False, False),
            'evening': TimeSlot('19:00', [], False, False),
            'night': TimeSlot('21:30', [], False, False),
            'as_needed': TimeSlot('as needed', [], False, False)
        }
        
        for med in prescription.medications:
            slots = self._determine_slots(med)
            
            for slot_name in slots:
                if slot_name == 'as_needed':
                    schedule['as_needed'].medications.append(self._med_to_dict(med))
                else:
                    slot = schedule[slot_name]
                    slot.medications.append(self._med_to_dict(med))
                    
                    # Update food constraints
                    if self._needs_food(med):
                        slot.food_required = True
                    if self._forbidden_food(med):
                        slot.food_forbidden = True
        
        # Apply preferences
        if preferences:
            schedule = self._apply_preferences(schedule, preferences)
        
        return schedule
    
    def _determine_slots(self, med: Medication) -> List[str]:
        """Determine time slots for medication."""
        freq = (med.frequency or '').upper()
        
        slot_map = {
            'OD': ['morning'],
            '1-0-0': ['morning'],
            '0-0-1': ['night'],
            '0-1-0': ['afternoon'],
            'BD': ['morning', 'night'],
            '1-0-1': ['morning', 'night'],
            'TID': ['morning', 'afternoon', 'night'],
            '1-1-1': ['morning', 'afternoon', 'night'],
            'QID': ['morning', 'afternoon', 'evening', 'night'],
            'HS': ['night'],
            'SOS': ['as_needed'],
            'STAT': ['morning'],
        }
        
        return slot_map.get(freq, ['as_needed'])
    
    def _needs_food(self, med: Medication) -> bool:
        """Check if medication should be taken with food."""
        if med.frequency and 'PC' in med.frequency.upper():
            return True
        if med.instructions and 'food' in med.instructions.lower():
            return 'with' in med.instructions.lower()
        
        # Common drugs that need food
        food_drugs = ['metformin', 'ibuprofen', 'aspirin', 'steroid']
        name = (med.generic_name or med.name or '').lower()
        return any(d in name for d in food_drugs)
    
    def _forbidden_food(self, med: Medication) -> bool:
        """Check if medication should be taken without food."""
        if med.frequency and 'AC' in med.frequency.upper():
            return True
        if med.instructions and 'empty stomach' in med.instructions.lower():
            return True
        return False
    
    def _med_to_dict(self, med: Medication) -> Dict:
        """Convert medication to schedule dict."""
        return {
            'name': med.name,
            'strength': med.strength,
            'instructions': med.instructions,
            'special': self._get_special_instructions(med)
        }
    
    def _get_special_instructions(self, med: Medication) -> str:
        """Get special scheduling instructions."""
        instructions = []
        
        if self._needs_food(med):
            instructions.append("Take with food")
        elif self._forbidden_food(med):
            instructions.append("Take before food/empty stomach")
        
        if 'sos' in (med.frequency or '').lower():
            instructions.append("As needed only")
        
        return "; ".join(instructions) if instructions else ""
    
    def _apply_preferences(self, schedule: Dict, preferences: Dict) -> Dict:
        """Apply user timing preferences."""
        if 'morning_time' in preferences:
            schedule['morning'].time = preferences['morning_time']
        if 'night_time' in preferences:
            schedule['night'].time = preferences['night_time']
        
        return schedule
    
    def check_conflicts(self, schedule: Dict) -> List[Dict]:
        """Check for scheduling conflicts."""
        conflicts = []
        
        # Check food conflicts
        for slot_name, slot in schedule.items():
            if slot.food_required and slot.food_forbidden:
                conflicts.append({
                    'type': 'food_conflict',
                    'slot': slot_name,
                    'message': 'Some meds need food, others need empty stomach'
                })
        
        return conflicts
    
    def optimize(self, schedule: Dict) -> Dict:
        """Optimize schedule for patient convenience."""
        # Group medications by compatibility
        # Suggest best times based on constraints
        return schedule