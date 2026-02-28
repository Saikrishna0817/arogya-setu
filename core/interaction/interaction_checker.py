"""Main drug interaction checking interface."""

from typing import List, Dict, Optional
import logging

from core.interaction.interaction_db_loader import InteractionDBLoader, SimpleInteractionDB
from core.interaction.interaction_scorer import InteractionScorer, SeverityLevel
from core.parsing.drug_name_resolver import DrugNameResolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionChecker:
    """Check drug-drug interactions in prescriptions."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = InteractionDBLoader()
        self.resolver = DrugNameResolver()
        
        # Try to load full database, fallback to simple
        if db_path:
            try:
                self.db.load_from_csv(db_path)
            except Exception as e:
                logger.warning(f"Could not load interaction DB: {e}")
        
        self.use_simple = len(self.db.interactions) == 0
    
    def check_pair(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check interaction between two specific drugs."""
        # Resolve to generic names
        r1 = self.resolver.resolve(drug1)
        r2 = self.resolver.resolve(drug2)
        
        generic1 = r1.get('generic') or drug1
        generic2 = r2.get('generic') or drug2
        
        if self.use_simple:
            result = SimpleInteractionDB.check(generic1, generic2)
        else:
            result = self.db.get_interaction(generic1, generic2)
            result = result[0] if result else None
        
        if result:
            return {
                'drug1': drug1,
                'drug2': drug2,
                'generic1': generic1,
                'generic2': generic2,
                **result
            }
        
        return None
    
    def check_prescription(self, medications: List[Dict]) -> Dict:
        """
        Check all interactions in a prescription.
        
        Args:
            medications: List of medication dicts with 'name' key
            
        Returns:
            Report with interactions and recommendations
        """
        drug_names = [m.get('name', m.get('generic_name', 'unknown')) 
                     for m in medications]
        
        interactions = []
        
        # Check all pairs
        for i, d1 in enumerate(drug_names):
            for d2 in drug_names[i+1:]:
                result = self.check_pair(d1, d2)
                if result:
                    interactions.append(result)
        
        # Prioritize by severity
        interactions = InteractionScorer.prioritize(interactions)
        
        # Categorize
        by_severity = {
            'contraindicated': [],
            'major': [],
            'moderate': [],
            'minor': []
        }
        
        for inter in interactions:
            sev = inter.get('severity', 'unknown').lower()
            if sev in by_severity:
                by_severity[sev].append(inter)
        
        # Generate summary
        summary = self._generate_summary(interactions)
        
        return {
            'interactions_found': len(interactions) > 0,
            'total_interactions': len(interactions),
            'by_severity': by_severity,
            'interactions': interactions,
            'summary': summary,
            'recommendations': self._get_recommendations(interactions)
        }
    
    def _generate_summary(self, interactions: List[Dict]) -> str:
        """Generate human-readable summary."""
        if not interactions:
            return "No significant drug interactions found."
        
        severe = [i for i in interactions 
                 if InteractionScorer.score(i) in 
                 [SeverityLevel.MAJOR, SeverityLevel.CONTRAINDICATED]]
        
        if severe:
            return f"⚠️ Found {len(severe)} serious interaction(s) requiring attention!"
        
        moderate = [i for i in interactions 
                   if InteractionScorer.score(i) == SeverityLevel.MODERATE]
        
        if moderate:
            return f"Found {len(moderate)} moderate interaction(s). Review recommended."
        
        return f"Found {len(interactions)} minor interaction(s). Generally manageable."
    
    def _get_recommendations(self, interactions: List[Dict]) -> List[str]:
        """Generate clinical recommendations."""
        recs = []
        
        for inter in interactions:
            sev = InteractionScorer.score(inter)
            
            if sev == SeverityLevel.CONTRAINDICATED:
                recs.append(f"AVOID combining {inter['drug1']} and {inter['drug2']}")
            elif sev == SeverityLevel.MAJOR:
                recs.append(f"Consider alternatives to {inter['drug1']} or {inter['drug2']}")
            elif sev == SeverityLevel.MODERATE:
                recs.append(f"Monitor closely: {inter['drug1']} + {inter['drug2']}")
        
        return list(set(recs))  # Remove duplicates