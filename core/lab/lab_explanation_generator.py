"""Generate explanations for lab reports."""

from typing import List, Dict
from core.lab.lab_extractor import LabItem
from core.lab.lab_rag import LabRAG
from core.llm.llm_client import LLMClient


class LabExplanationGenerator:
    """Generate patient-friendly lab explanations."""
    
    def __init__(self):
        self.rag = LabRAG()
        self.llm = LLMClient()
    
    def generate(self, lab_items: List[LabItem], 
                 style: str = 'simple') -> str:
        """
        Generate explanation for lab results.
        
        Args:
            lab_items: Extracted lab values
            style: 'simple', 'detailed', or 'technical'
            
        Returns:
            Explanation text
        """
        # Build prompt with RAG context
        context = self.rag.generate_context(lab_items)
        
        # Categorize results
        abnormal = [item for item in lab_items if item.flag]
        normal = [item for item in lab_items if not item.flag]
        
        prompt = f"""You are a medical assistant explaining lab results to a patient.

LAB RESULTS SUMMARY:
Total tests: {len(lab_items)}
Normal: {len(normal)}
Abnormal: {len(abnormal)}

DETAILED RESULTS:
"""
        
        for item in lab_items:
            status = "⚠️ ABNORMAL" if item.flag else "✅ Normal"
            prompt += f"\n{item.name}: {item.value} {item.unit} ({status})"
            if item.flag:
                direction = "HIGH" if item.flag == 'H' else "LOW"
                prompt += f" - {direction}"
        
        prompt += f"\n\nBACKGROUND INFORMATION:\n{context}"
        
        prompt += f"""
\n\nPlease provide a {style} explanation that:
1. Highlights which values need attention
2. Explains what each abnormal value might mean in simple terms
3. Suggests general lifestyle advice (diet, exercise)
4. Emphasizes that they should discuss with their doctor
5. Do not diagnose or suggest specific treatments

Generate the explanation:"""
        
        return self.llm.generate(prompt, max_tokens=1000, temperature=0.3)
    
    def generate_structured(self, lab_items: List[LabItem]) -> Dict:
        """Generate structured explanation."""
        return {
            'summary': self.generate(lab_items, style='simple'),
            'detailed': self.generate(lab_items, style='detailed'),
            'abnormal_count': len([i for i in lab_items if i.flag]),
            'items': [
                {
                    'name': item.name,
                    'value': item.value,
                    'unit': item.unit,
                    'status': 'abnormal' if item.flag else 'normal',
                    'direction': 'high' if item.flag == 'H' else ('low' if item.flag == 'L' else None),
                    'explanation': self.rag.retrieve(item.name)
                }
                for item in lab_items
            ]
        }