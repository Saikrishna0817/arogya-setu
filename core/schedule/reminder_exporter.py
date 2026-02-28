"""Export reminders to calendar formats."""

from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
import json


class ReminderExporter:
    """Export medication reminders to various formats."""
    
    @staticmethod
    def to_ical(schedule: Dict[str, List], 
                filename: str = "medication_schedule.ics") -> str:
        """Generate iCalendar format."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Vernacular Medical Parser//Medication Schedule//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        start_date = datetime.now()
        
        for slot, items in schedule.items():
            for item in items:
                # Create event for each medication
                event_date = start_date.strftime('%Y%m%d')
                
                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{item.medication.replace(' ', '_')}@vernacular",
                    f"DTSTART;VALUE=DATE:{event_date}",
                    f"RRULE:FREQ=DAILY;UNTIL={(start_date + timedelta(days=30)).strftime('%Y%m%d')}",
                    f"SUMMARY:Take {item.medication}",
                    f"DESCRIPTION:Strength: {item.strength or 'N/A'}\\n"
                    f"Instructions: {item.special_instructions or 'None'}",
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:Time to take {item.medication}",
                    "TRIGGER:-PT15M",  # 15 min reminder
                    "END:VALARM",
                    "END:VEVENT"
                ])
        
        lines.append("END:VCALENDAR")
        
        ical_content = "\r\n".join(lines)
        
        # Save to file
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ical_content)
        
        return str(output_path)
    
    @staticmethod
    def to_json(schedule: Dict[str, List], 
                timeline: List[Dict],
                filename: str = "schedule.json") -> str:
        """Export to JSON format."""
        data = {
            'generated_at': datetime.now().isoformat(),
            'daily_schedule': {},
            'timeline': timeline
        }
        
        for slot, items in schedule.items():
            data['daily_schedule'][slot] = [
                {
                    'medication': item.medication,
                    'strength': item.strength,
                    'time': item.time_display,
                    'with_food': item.with_food,
                    'instructions': item.special_instructions
                }
                for item in items
            ]
        
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return str(output_path)