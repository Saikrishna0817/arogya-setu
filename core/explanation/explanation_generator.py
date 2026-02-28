"""Generate patient-friendly explanations from prescriptions."""

import json
from typing import Dict, Optional
import logging
from datetime import datetime

from core.parsing.prescription_parser import Prescription, Medication
from core.llm.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Generate clear explanations from structured prescriptions."""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.llm_client = LLMClient() if use_llm else None
        
        # Template-based explanations as fallback
        self.templates = {
            'intro': "This prescription contains {count} medication(s):",
            'medication': "{name} {strength}: Take {frequency} for {duration}. {purpose}",
            'warning': "Important: Take exactly as prescribed. Do not stop without consulting your doctor.",
            'footer': "If you experience side effects, contact your doctor immediately."
        }
    
    def generate(self, prescription: Prescription, 
                 style: str = 'simple',
                 include_warnings: bool = True) -> str:
        """
        Generate explanation script.
        
        Args:
            prescription: Parsed prescription
            style: 'simple', 'detailed', or 'technical'
            include_warnings: Add safety warnings
            
        Returns:
            Explanation text
        """
        if self.use_llm and self.llm_client:
            return self._generate_llm(prescription, style, include_warnings)
        else:
            return self._generate_template(prescription, include_warnings)
    
    def _generate_llm(self, prescription: Prescription, 
                      style: str, include_warnings: bool) -> str:
        """Use LLM for natural explanation."""
        # Build prompt
        prompt = self._build_prompt(prescription, style, include_warnings)
        
        try:
            response = self.llm_client.generate(prompt, max_tokens=800, temperature=0.3)
            return self._post_process(response)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_template(prescription, include_warnings)
    
    def _build_prompt(self, prescription: Prescription, 
                      style: str, include_warnings: bool) -> str:
        """Build LLM prompt."""
        meds_text = "\n".join([
            f"- {m.name} {m.strength or ''}: {m.frequency_normalized or m.frequency or 'as directed'}, "
            f"for {m.duration or 'specified duration'}. "
            f"Instructions: {m.instructions or 'None'}"
            for m in prescription.medications
        ])
        
        prompt = f"""You are a medical assistant helping a patient understand their prescription. 
Write a clear, friendly explanation in English.

PRESCRIPTION DETAILS:
Doctor: {prescription.doctor_name or 'Not specified'}
Date: {prescription.date or 'Not specified'}
Medications:
{meds_text}

GUIDELINES:
- Use simple language a 10th-grade student can understand
- Explain what each medicine is likely for (based on common uses)
- Emphasize the importance of following dosage exactly
- {'Include safety warnings about side effects and when to call doctor' if include_warnings else ''}
- Do NOT suggest the prescription is wrong or change any dosages
- Add disclaimer that this is educational, not medical advice

STYLE: {style}

Generate the explanation:"""
        
        return prompt
    
    def _generate_template(self, prescription: Prescription, 
                          include_warnings: bool) -> str:
        """Fallback template-based generation."""
        lines = []
        
        # Header
        lines.append(f"Prescription from {prescription.doctor_name or 'your doctor'}")
        if prescription.date:
            lines.append(f"Date: {prescription.date}")
        lines.append("")
        
        # Medications
        lines.append(self.templates['intro'].format(count=len(prescription.medications)))
        lines.append("")
        
        for i, med in enumerate(prescription.medications, 1):
            purpose = self._guess_purpose(med.generic_name or med.name)
            
            line = self.templates['medication'].format(
                name=med.name,
                strength=med.strength or '',
                frequency=med.frequency_normalized or med.frequency or 'as directed',
                duration=med.duration or 'the full course',
                purpose=purpose
            )
            lines.append(f"{i}. {line}")
            
            if med.instructions:
                lines.append(f"   Special instructions: {med.instructions}")
            lines.append("")
        
        # Warnings
        if include_warnings:
            lines.append(self.templates['warning'])
            lines.append(self.templates['footer'])
        
        return "\n".join(lines)
    
    def _guess_purpose(self, drug_name: Optional[str]) -> str:
        """Infer likely purpose from drug name."""
        if not drug_name:
            return ""
        
        purposes = {
            'Amlodipine': 'for blood pressure',
            'Metoprolol': 'for heart rate and blood pressure',
            'Losartan': 'for blood pressure',
            'Metformin': 'for blood sugar control',
            'Glimepiride': 'for diabetes',
            'Paracetamol': 'for pain and fever',
            'Ibuprofen': 'for pain and inflammation',
            'Amoxicillin': 'for bacterial infection',
            'Omeprazole': 'for stomach acid/heartburn',
            'Pantoprazole': 'for stomach protection',
        }
        
        for drug, purpose in purposes.items():
            if drug.lower() in drug_name.lower():
                return f"This is typically used {purpose}."
        
        return "Please ask your doctor what this medicine is for."
    
    def _post_process(self, text: str) -> str:
        """Clean up LLM output."""
        # Remove any "Patient:" or "Doctor:" roleplay prefixes
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            if line.strip().startswith(('Patient:', 'Doctor:', 'Assistant:')):
                continue
            cleaned.append(line)
        
        text = '\n'.join(cleaned)
        
        # Ensure disclaimer present
        if "not medical advice" not in text.lower():
            text += "\n\n[This is an educational explanation, not medical advice. Consult your doctor for specific guidance.]"
        
        return text.strip()
    
    def generate_structured(self, prescription: Prescription) -> Dict:
        """Generate structured explanation for UI rendering."""
        return {
            'summary': self.generate(prescription, style='simple'),
            'detailed': self.generate(prescription, style='detailed'),
            'medications': [
                {
                    'name': m.name,
                    'explanation': self._explain_medication(m),
                    'warnings': self._get_warnings(m)
                }
                for m in prescription.medications
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def _explain_medication(self, med: Medication) -> str:
        """Explain single medication."""
        parts = []
        
        if med.generic_name and med.generic_name != med.name:
            parts.append(f"Generic name: {med.generic_name}")
        
        parts.append(f"How to take: {med.frequency_normalized or 'As directed by doctor'}")
        
        if med.duration:
            parts.append(f"Duration: {med.duration}")
        
        if med.instructions:
            parts.append(f"Important: {med.instructions}")
        
        return " ".join(parts)
    
    def _get_warnings(self, med: Medication) -> list:
        """Get safety warnings for medication."""
        warnings = []
        
        # Check for high dose
        from config.dosage_limits import DOSAGE_LIMITS
        if med.generic_name in DOSAGE_LIMITS:
            limits = DOSAGE_LIMITS[med.generic_name]
            if med.strength_value and med.strength_value > limits.get('max_daily_mg', 9999):
                warnings.append(f"Dose appears high. Verify with doctor.")
        
        # Common drug warnings
        if 'Paracetamol' in (med.generic_name or med.name):
            warnings.append("Do not exceed 4g per day. Check other medicines for paracetamol content.")
        
        if 'Metformin' in (med.generic_name or med.name):
            warnings.append("Take with food to avoid stomach upset.")
        
        return warnings