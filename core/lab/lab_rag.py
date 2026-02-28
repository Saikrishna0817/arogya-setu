"""RAG pipeline for lab report explanations using your knowledge base."""

from typing import List, Dict, Optional
from pathlib import Path
import logging

from core.lab.lab_extractor import LabItem
from config.paths import Paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabRAG:
    """RAG using your markdown knowledge base."""
    
    def __init__(self, kb_dir: Optional[Path] = None):
        self.kb_dir = kb_dir or Paths.DATA_DIR / 'lab_knowledge_base'
        self.knowledge_base: Dict[str, str] = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load your .md files."""
        if not self.kb_dir.exists():
            logger.warning(f"KB folder not found: {self.kb_dir}")
            return
        
        for file_path in self.kb_dir.glob('*.md'):
            test_name = file_path.stem  # e.g., "hemoglobin", "glucose"
            content = file_path.read_text(encoding='utf-8')
            self.knowledge_base[test_name.lower()] = content
            logger.debug(f"Loaded KB article: {test_name}")
        
        logger.info(f"Loaded {len(self.knowledge_base)} KB articles from {self.kb_dir}")
    
    def retrieve(self, test_name: str) -> str:
        """Retrieve explanation for test."""
        # Direct match
        if test_name.lower() in self.knowledge_base:
            return self.knowledge_base[test_name.lower()]
        
        # Fuzzy match
        for key, content in self.knowledge_base.items():
            if key in test_name.lower() or test_name.lower() in key:
                return content
        
        return f"No detailed information available for {test_name}."
    
    def generate_context(self, lab_items: List[LabItem]) -> str:
        """Generate context string for LLM from your KB."""
        contexts = []
        
        for item in lab_items:
            kb_content = self.retrieve(item.name)
            
            context = f"""
Test: {item.name}
Value: {item.value} {item.unit}
Reference Range: {item.ref_low}-{item.ref_high} {item.unit}
Status: {'Critical' if item.flag == 'C' else ('High' if item.flag == 'H' else ('Low' if item.flag == 'L' else 'Normal'))}

Clinical Context:
{item.interpretation or 'No specific interpretation available.'}

Detailed Information:
{kb_content}
"""
            contexts.append(context)
        
        return "\n---\n".join(contexts)
    
    def get_recommendations(self, item: LabItem) -> List[str]:
        """Get recommendations based on flag."""
        recommendations = []
        
        if item.flag == 'C':  # Critical
            recommendations.append("URGENT: Consult doctor immediately")
            recommendations.append("Repeat test to confirm")
        elif item.flag == 'H':
            recommendations.append("Monitor closely")
            if 'glucose' in item.name.lower():
                recommendations.append("Consider diabetes screening")
            elif 'cholesterol' in item.name.lower():
                recommendations.append("Dietary modifications recommended")
        elif item.flag == 'L':
            recommendations.append("Follow-up testing advised")
            if 'hemoglobin' in item.name.lower():
                recommendations.append("Iron supplementation may be needed")
        
        return recommendations