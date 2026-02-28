"""Parse and validate LLM responses."""

import json
import re
from typing import Dict, Any, Optional


class ResponseParser:
    """Parse structured data from LLM text responses."""
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict]:
        """Extract JSON from text (handles markdown code blocks)."""
        # Try to find JSON in code blocks
        patterns = [
            r'```json\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'\{.*\}'  # Last resort - greedy match
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        
        return None
    
    @staticmethod
    def extract_list(text: str) -> list:
        """Extract bullet points or numbered list."""
        lines = text.split('\n')
        items = []
        
        for line in lines:
            # Match bullet points or numbered items
            match = re.match(r'^\s*(?:[-•*]|\d+[.)])\s*(.+)$', line)
            if match:
                items.append(match.group(1).strip())
        
        return items
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """Extract sections by headers."""
        sections = {}
        current_section = 'general'
        current_content = []
        
        for line in text.split('\n'):
            # Check for header (all caps, or ending with :)
            if re.match(r'^[A-Z][A-Z\s]+:$', line) or re.match(r'^[A-Za-z\s]+:$', line):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip(':').lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def validate_medical_response(text: str) -> Dict[str, Any]:
        """Check response for safety issues."""
        issues = []
        
        # Check for disallowed content
        dangerous_patterns = [
            r'stop taking',
            r'do not take',
            r'ignore.*doctor',
            r'change.*dose',
            r'double.*dose',
            r' overdose'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Flagged pattern: {pattern}")
        
        # Check for disclaimer
        has_disclaimer = any(word in text.lower() for word in 
                           ['disclaimer', 'not medical advice', 'consult doctor'])
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'has_disclaimer': has_disclaimer,
            'length': len(text)
        }