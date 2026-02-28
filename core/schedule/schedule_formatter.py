"""Format schedules for different outputs."""

from typing import Dict, List
import pandas as pd
from datetime import datetime


class ScheduleFormatter:
    """Format medication schedules."""
    
    @staticmethod
    def to_table(schedule: Dict[str, List]) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        rows = []
        
        for slot, items in schedule.items():
            for item in items:
                rows.append({
                    'Time': item.time_display,
                    'Medication': item.medication,
                    'Strength': item.strength or '',
                    'With Food': 'Yes' if item.with_food else 'No',
                    'Instructions': item.special_instructions or ''
                })
        
        df = pd.DataFrame(rows)
        return df.sort_values('Time')
    
    @staticmethod
    def to_text(schedule: Dict[str, List]) -> str:
        """Convert to readable text."""
        lines = ["Daily Medication Schedule", "=" * 40, ""]
        
        for slot in ['morning', 'afternoon', 'evening', 'night', 'as_needed']:
            items = schedule.get(slot, [])
            if not items:
                continue
            
            lines.append(f"\n{slot.upper()}")
            lines.append("-" * 20)
            
            for item in items:
                food_note = " (with food)" if item.with_food else ""
                lines.append(f"• {item.time_display}: {item.medication} {item.strength or ''}{food_note}")
                if item.special_instructions:
                    lines.append(f"  Note: {item.special_instructions}")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(schedule: Dict[str, List]) -> Dict:
        """Convert to JSON-serializable dict."""
        result = {}
        
        for slot, items in schedule.items():
            result[slot] = [
                {
                    'medication': item.medication,
                    'strength': item.strength,
                    'time': item.time_display,
                    'with_food': item.with_food,
                    'instructions': item.special_instructions
                }
                for item in items
            ]
        
        return result