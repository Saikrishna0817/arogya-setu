"""Build structured prompts for different use cases."""

from typing import Dict, List, Optional
from core.parsing.prescription_parser import Prescription


class PromptBuilder:
    """Build prompts for various medical tasks."""
    
    @staticmethod
    def prescription_explanation(prescription: Prescription, 
                                  style: str = 'simple') -> str:
        """Build prompt for prescription explanation."""
        meds = "\n".join([
            f"- {m.name} ({m.strength or 'unknown strength'}): "
            f"{m.frequency_normalized or m.frequency or 'as directed'}, "
            f"for {m.duration or 'specified time'}"
            for m in prescription.medications
        ])
        
        prompts = {
            'simple': f"""Explain this prescription to a patient with 10th-grade education:

Medications:
{meds}

Use simple language. Explain what each medicine is for. Include safety reminders. Do not suggest changes to the prescription.

Explanation:""",
            
            'detailed': f"""Provide a detailed explanation of this prescription:

Doctor: {prescription.doctor_name or 'Unknown'}
Date: {prescription.date or 'Unknown'}
Diagnosis: {prescription.diagnosis or 'Not specified'}

Medications:
{meds}

Include:
1. Purpose of each medication
2. How and when to take
3. Common side effects to watch for
4. When to contact doctor

Explanation:""",
            
            'technical': f"""Clinical summary of prescription:

{meds}

Provide pharmacological overview and monitoring parameters."""
        }
        
        return prompts.get(style, prompts['simple'])
    
    @staticmethod
    def drug_interaction_check(drug_list: List[str]) -> str:
        """Build prompt for interaction checking."""
        drugs = ", ".join(drug_list)
        
        return f"""Check for drug interactions between: {drugs}

List any significant interactions, severity (minor/moderate/major), and recommendations. If no interactions, state "No significant interactions found."

Interactions:"""
    
    @staticmethod
    def lab_report_summary(lab_values: List[Dict]) -> str:
        """Build prompt for lab report interpretation."""
        values_text = "\n".join([
            f"- {v['name']}: {v['value']} {v['unit']} "
            f"(Normal: {v.get('ref_low', '?')}-{v.get('ref_high', '?')})"
            for v in lab_values
        ])
        
        return f"""Interpret these lab results for a patient:

{values_text}

Highlight any abnormal values, explain what they might mean in simple terms, and suggest general lifestyle advice. Include disclaimer that this is not medical advice.

Interpretation:"""
    
    @staticmethod
    def dosage_validation(drug: str, prescribed_dose: float, 
                         standard_dose: float) -> str:
        """Build prompt for dosage validation."""
        return f"""The prescribed dose of {drug} is {prescribed_dose}mg, 
while standard is {standard_dose}mg. 

Is this concerning? Provide brief clinical context."""