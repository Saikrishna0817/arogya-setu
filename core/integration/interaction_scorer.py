"""Score and categorize interaction severity."""

from enum import Enum
from typing import Dict, List


class SeverityLevel(Enum):
    """Interaction severity levels."""
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    CONTRAINDICATED = 4


class InteractionScorer:
    """Score interaction severity and clinical significance."""
    
    SEVERITY_WEIGHTS = {
        'minor': SeverityLevel.MINOR,
        'moderate': SeverityLevel.MODERATE,
        'major': SeverityLevel.MAJOR,
        'contraindicated': SeverityLevel.CONTRAINDICATED,
        'contraindication': SeverityLevel.CONTRAINDICATED,
        'severe': SeverityLevel.MAJOR
    }
    
    @classmethod
    def score(cls, interaction: Dict) -> SeverityLevel:
        """Determine severity level."""
        severity_str = interaction.get('severity', 'unknown').lower()
        return cls.SEVERITY_WEIGHTS.get(severity_str, SeverityLevel.MINOR)
    
    @classmethod
    def get_color(cls, level: SeverityLevel) -> str:
        """Get display color for severity."""
        colors = {
            SeverityLevel.MINOR: '#FFA500',  # Orange
            SeverityLevel.MODERATE: '#FF8C00',  # Dark orange
            SeverityLevel.MAJOR: '#FF4500',  # Red-orange
            SeverityLevel.CONTRAINDICATED: '#FF0000'  # Red
        }
        return colors.get(level, '#808080')
    
    @classmethod
    def get_icon(cls, level: SeverityLevel) -> str:
        """Get icon for severity."""
        icons = {
            SeverityLevel.MINOR: '⚠️',
            SeverityLevel.MODERATE: '⚠️⚠️',
            SeverityLevel.MAJOR: '⛔',
            SeverityLevel.CONTRAINDICATED: '🚫'
        }
        return icons.get(level, '❓')
    
    @classmethod
    def prioritize(cls, interactions: List[Dict]) -> List[Dict]:
        """Sort interactions by severity."""
        scored = [(cls.score(i), i) for i in interactions]
        scored.sort(key=lambda x: x[0].value, reverse=True)
        return [i for _, i in scored]
    
    @classmethod
    def clinical_significance(cls, interaction: Dict) -> str:
        """Assess clinical significance."""
        level = cls.score(interaction)
        
        significance = {
            SeverityLevel.MINOR: "Monitor - usually manageable",
            SeverityLevel.MODERATE: "Action needed - may require dose adjustment",
            SeverityLevel.MAJOR: "Significant risk - consider alternatives",
            SeverityLevel.CONTRAINDICATED: "Avoid combination - serious harm risk"
        }
        
        return significance.get(level, "Unknown significance")