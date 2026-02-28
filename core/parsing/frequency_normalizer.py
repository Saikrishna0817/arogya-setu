"""Normalize prescription frequency codes to readable text."""

from typing import Dict, Optional
from config.languages import MEDICAL_TERMS


class FrequencyNormalizer:
    """Convert frequency codes to multiple languages."""
    
    def __init__(self):
        self.english_map = {
            'OD': 'once daily',
            'BD': 'twice daily',
            'TID': 'three times daily',
            'QID': 'four times daily',
            'HS': 'at bedtime',
            'SOS': 'as needed',
            'AC': 'before meals',
            'PC': 'after meals',
            'STAT': 'immediately',
            'OM': 'every morning',
            'ON': 'every night',
            '1-0-1': 'morning and night',
            '1-0-0': 'morning only',
            '0-0-1': 'night only',
            '0-1-0': 'afternoon only',
        }
    
    def normalize(self, code: str, language: str = 'en') -> Optional[str]:
        """
        Normalize frequency code to specified language.
        
        Args:
            code: Frequency code (OD, BD, etc.)
            language: Target language code
            
        Returns:
            Normalized string or None
        """
        if not code:
            return None
        
        code_upper = code.upper()
        
        # Get English first
        english = self.english_map.get(code_upper, code)
        
        if language == 'en':
            return english
        
        # Translate using medical terms dictionary
        if code_upper in MEDICAL_TERMS and language in MEDICAL_TERMS[code_upper]:
            return MEDICAL_TERMS[code_upper][language]
        
        # Fallback to English
        return english
    
    def get_schedule(self, code: str) -> Dict[str, bool]:
        """Get boolean schedule for time slots."""
        code_upper = code.upper() if code else ''
        
        schedule = {
            'morning': False,
            'afternoon': False,
            'evening': False,
            'night': False
        }
        
        if code_upper in ['OD', '1-0-0', 'OM']:
            schedule['morning'] = True
        elif code_upper in ['HS', '0-0-1', 'ON']:
            schedule['night'] = True
        elif code_upper in ['BD', '1-0-1']:
            schedule['morning'] = True
            schedule['night'] = True
        elif code_upper in ['TID']:
            schedule['morning'] = True
            schedule['afternoon'] = True
            schedule['night'] = True
        elif code_upper in ['QID']:
            schedule['morning'] = True
            schedule['afternoon'] = True
            schedule['evening'] = True
            schedule['night'] = True
        
        return schedule