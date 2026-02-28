"""Generate medication schedules from prescriptions."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.parsing.prescription_parser import Prescription, Medication
from core.parsing.frequency_normalizer import FrequencyNormalizer


@dataclass
class ScheduleItem:
    """Single schedule entry."""
    medication: str
    strength: Optional[str]
    time_slot: str  # morning, afternoon, evening, night
    time_display: str  # e.g., "8:00 AM"
    with_food: bool
    special_instructions: Optional[str]


class ScheduleGenerator:
    """Generate daily medication schedules."""
    
    TIME_SLOTS = {
        'morning': '08:00 AM',
        'afternoon': '01:00 PM',
        'evening': '06:00 PM',
        'night': '09:00 PM'
    }
    
    def __init__(self):
        self.freq_norm = FrequencyNormalizer()
    
    def generate(self, prescription: Prescription,
                 preferences: Optional[Dict] = None) -> Dict[str, List[ScheduleItem]]:
        """
        Generate schedule organized by time slot.
        
        Args:
            prescription: Parsed prescription
            preferences: Optional time preferences
            
        Returns:
            Dict of time_slot -> list of medications
        """
        schedule = {
            'morning': [],
            'afternoon': [],
            'evening': [],
            'night': [],
            'as_needed': []
        }
        
        for med in prescription.medications:
            slots = self._determine_slots(med)
            
            for slot in slots:
                if slot == 'as_needed':
                    schedule['as_needed'].append(self._create_item(med, slot))
                else:
                    schedule[slot].append(self._create_item(med, slot))
        
        # Sort each slot by medication name
        for slot in schedule:
            schedule[slot].sort(key=lambda x: x.medication)
        
        return schedule
    
    def _determine_slots(self, med: Medication) -> List[str]:
        """Determine time slots from frequency."""
        if not med.frequency:
            return ['as_needed']
        
        freq = med.frequency.upper()
        
        # Map frequencies to slots
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
            'STAT': ['morning'],  # Immediate, but schedule for convenience
            'OM': ['morning'],
            'ON': ['night']
        }
        
        return slot_map.get(freq, ['as_needed'])
    
    def _create_item(self, med: Medication, slot: str) -> ScheduleItem:
        """Create schedule item."""
        # Determine if with food
        with_food = False
        if med.frequency:
            freq = med.frequency.upper()
            if 'PC' in freq or 'AC' in freq:
                with_food = True
        if med.instructions and 'food' in med.instructions.lower():
            with_food = True
        
        # Special instructions
        special = med.instructions if med.instructions else None
        
        return ScheduleItem(
            medication=med.name,
            strength=med.strength,
            time_slot=slot,
            time_display=self.TIME_SLOTS.get(slot, 'As needed'),
            with_food=with_food,
            special_instructions=special
        )
    
    def generate_timeline(self, prescription: Prescription, 
                         days: int = 7) -> List[Dict]:
        """Generate day-by-day timeline for multi-day prescriptions."""
        timeline = []
        base_schedule = self.generate(prescription)
        
        start_date = datetime.now()
        
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            day_schedule = {
                'date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'slots': {}
            }
            
            # Copy schedule for this day
            for slot, items in base_schedule.items():
                day_schedule['slots'][slot] = [
                    {
                        'medication': item.medication,
                        'strength': item.strength,
                        'time': item.time_display,
                        'taken': False  # For tracking
                    }
                    for item in items
                ]
            
            timeline.append(day_schedule)
        
        return timeline