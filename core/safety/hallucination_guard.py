"""Prevent LLM hallucinations in medical context."""

import re
from typing import Dict, List, Optional, Tuple


class HallucinationGuard:
    """Guard against medical misinformation."""
    
    # Dangerous patterns that suggest hallucination
    DANGEROUS_PATTERNS = [
        r'stop taking\s+\w+',  # Telling patient to stop medication
        r'do not take\s+\w+',
        r'ignore.*doctor',
        r'change your dose to\s+\d+',  # Suggesting dose changes
        r'increase\s+\w+\s+to\s+\d+',
        r'decrease\s+\w+\s+to\s+\d+',
        r'double the dose',
        r'half the dose',
        r'take\s+\w+\s+instead of\s+\w+',  # Suggesting substitutions
        r'diagnosis[:\s]+\w+',  # Making definitive diagnoses
        r'you have\s+\w+',  # Diagnosing
        r'cure[:\s]+\w+',
        r'guaranteed',
        r'100% effective',
        r'no side effects',
        r'completely safe',
    ]
    
    # Required safety elements
    REQUIRED_ELEMENTS = [
        'consult',
        'doctor',
        'physician',
        'healthcare',
        'medical advice',
        'not.*substitute',
        'not.*replace'
    ]
    
    # Facts that must be verified
    VERIFICATION_TRIGGERS = {
        'dosage': r'\d+\s*mg',
        'frequency': r'(od|bd|tds|qid)',
        'duration': r'\d+\s*days?'
    }
    
    def __init__(self):
        self.violations = []
        self.warnings = []
    
    def check(self, text: str, original_prescription: Optional[Dict] = None) -> Dict:
        """
        Check text for hallucinations.
        
        Args:
            text: LLM generated text
            original_prescription: Original parsed prescription for verification
            
        Returns:
            Safety report
        """
        self.violations = []
        self.warnings = []
        
        # Check dangerous patterns
        self._check_dangerous_patterns(text)
        
        # Check required elements
        has_disclaimer = self._check_required_elements(text)
        
        # Verify facts against prescription
        if original_prescription:
            self._verify_facts(text, original_prescription)
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(has_disclaimer)
        
        return {
            'safe': len(self.violations) == 0 and safety_score > 0.7,
            'safety_score': safety_score,
            'violations': self.violations,
            'warnings': self.warnings,
            'has_disclaimer': has_disclaimer,
            'recommendations': self._generate_recommendations()
        }
    
    def _check_dangerous_patterns(self, text: str):
        """Check for dangerous advice."""
        text_lower = text.lower()
        
        for pattern in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                self.violations.append({
                    'type': 'dangerous_advice',
                    'pattern': pattern,
                    'matched_text': match.group(0),
                    'severity': 'critical'
                })
    
    def _check_required_elements(self, text: str) -> bool:
        """Check for required safety elements."""
        text_lower = text.lower()
        
        found_elements = []
        for element in self.REQUIRED_ELEMENTS:
            if re.search(element, text_lower):
                found_elements.append(element)
        
        # Need at least 2 safety elements
        return len(found_elements) >= 2
    
    def _verify_facts(self, text: str, prescription: Dict):
        """Verify that facts match prescription."""
        # Extract mentioned dosages from text
        mentioned_doses = re.findall(r'(\d+)\s*mg', text.lower())
        
        # Compare with prescription
        actual_doses = []
        for med in prescription.get('medications', []):
            dose = med.get('strength_value')
            if dose:
                actual_doses.append(str(int(dose)))
        
        # Check for mismatches
        for dose in mentioned_doses:
            if dose not in actual_doses:
                self.warnings.append({
                    'type': 'unverified_dosage',
                    'message': f'Mentioned dose {dose}mg not found in prescription',
                    'severity': 'medium'
                })
    
    def _calculate_safety_score(self, has_disclaimer: bool) -> float:
        """Calculate overall safety score."""
        score = 1.0
        
        # Critical violations
        score -= len([v for v in self.violations if v['severity'] == 'critical']) * 0.5
        
        # Warnings
        score -= len(self.warnings) * 0.1
        
        # Disclaimer bonus
        if not has_disclaimer:
            score -= 0.3
        
        return max(0.0, score)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate fix recommendations."""
        recs = []
        
        if self.violations:
            recs.append("Remove dangerous advice patterns")
            recs.append("Add mandatory medical disclaimer")
        
        if self.warnings:
            recs.append("Verify all medical facts against source")
        
        return recs
    
    def sanitize(self, text: str) -> str:
        """Remove dangerous content."""
        sanitized = text
        
        for pattern in self.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def add_disclaimer(self, text: str) -> str:
        """Add disclaimer if missing."""
        if any(word in text.lower() for word in ['disclaimer', 'not medical advice']):
            return text
        
        disclaimer = """
        
---
**Medical Disclaimer**: This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
"""
        
        return text + disclaimer