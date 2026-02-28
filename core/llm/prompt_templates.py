"""Centralized prompt templates for all LLM operations."""

from typing import Dict


class PromptTemplates:
    """Collection of prompt templates."""
    
    # Prescription explanations
    PRESCRIPTION_SIMPLE = """Explain this prescription to a patient with 10th-grade education level. Use simple, friendly language.

PRESCRIPTION:
{medications}

GUIDELINES:
- Explain what each medicine is likely for (based on common uses)
- Explain when and how to take each medicine
- Mention common side effects to watch for
- Emphasize importance of completing the full course
- Add strong disclaimer that this is not medical advice

Generate explanation:"""

    PRESCRIPTION_DETAILED = """Provide a detailed medical explanation of this prescription for an educated patient.

PRESCRIPTION:
Doctor: {doctor}
Date: {date}
Diagnosis: {diagnosis}

Medications:
{medications}

Include:
1. Pharmacological mechanism of each drug
2. Expected therapeutic effects
3. Common and serious adverse effects
4. Drug interactions to avoid
5. Monitoring parameters

Explanation:"""

    # Lab reports
    LAB_SUMMARY = """Interpret these lab results for a patient:

{lab_values}

For each abnormal value:
- Explain what it means in simple terms
- Mention possible causes (without diagnosing)
- Suggest when to follow up with doctor

Keep explanations non-alarming but accurate. Include disclaimer.

Interpretation:"""

    # Drug interactions
    INTERACTION_CHECK = """Analyze potential drug interactions:

DRUGS: {drug_list}

For each interaction found:
1. Severity (contraindicated/major/moderate/minor)
2. Mechanism
3. Clinical effects
4. Management recommendation

If no interactions, state "No significant interactions identified."

Analysis:"""

    # Dosage validation
    DOSAGE_VALIDATION = """Validate this dosage:
Drug: {drug}
Prescribed dose: {prescribed}
Standard range: {standard}
Patient: {patient_context}

Is this dose appropriate? If not, what are the concerns?
Provide brief clinical reasoning.

Validation:"""

    # Safety prompts
    SAFETY_PREFIX = """You are a medical information assistant. 
CRITICAL RULES:
- NEVER tell patients to stop or change prescribed medications
- NEVER provide definitive diagnoses
- ALWAYS recommend consulting healthcare providers
- ALWAYS include medical disclaimer
- NEVER suggest dosage changes

"""

    @classmethod
    def get_prompt(cls, template_name: str, **kwargs) -> str:
        """Get formatted prompt."""
        template = getattr(cls, template_name, "")
        
        # Add safety prefix for medical prompts
        if 'PRESCRIPTION' in template_name or 'LAB' in template_name:
            template = cls.SAFETY_PREFIX + template
        
        return template.format(**kwargs)
    
    @classmethod
    def list_templates(cls) -> Dict[str, str]:
        """List available templates."""
        return {
            'prescription_simple': cls.PRESCRIPTION_SIMPLE,
            'prescription_detailed': cls.PRESCRIPTION_DETAILED,
            'lab_summary': cls.LAB_SUMMARY,
            'interaction_check': cls.INTERACTION_CHECK,
            'dosage_validation': cls.DOSAGE_VALIDATION
        }