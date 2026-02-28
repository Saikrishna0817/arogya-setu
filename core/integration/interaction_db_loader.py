"""Load and manage drug interaction databases."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
import pickle
import logging

from config.paths import Paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionDBLoader:
    """Load DrugBank, OpenFDA, or custom interaction data."""
    
    def __init__(self):
        self.interactions: Dict[str, List[Dict]] = {}  # drug_pair -> interactions
        self.drugs: Set[str] = set()
    
    def load_from_csv(self, csv_path: Path) -> 'InteractionDBLoader':
        """Load cleaned interaction CSV."""
        if not csv_path.exists():
            logger.warning(f"Interaction CSV not found: {csv_path}")
            return self
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                drug1 = row.get('drug1', '').lower()
                drug2 = row.get('drug2', '').lower()
                
                if not drug1 or not drug2:
                    continue
                
                pair = tuple(sorted([drug1, drug2]))
                
                interaction = {
                    'severity': row.get('severity', 'unknown'),
                    'description': row.get('description', ''),
                    'mechanism': row.get('mechanism', ''),
                    'management': row.get('management', '')
                }
                
                if pair not in self.interactions:
                    self.interactions[pair] = []
                self.interactions[pair].append(interaction)
                
                self.drugs.add(drug1)
                self.drugs.add(drug2)
        
        logger.info(f"Loaded {len(self.interactions)} interactions")
        return self
    
    def load_from_drugbank(self, drugbank_path: Path) -> 'InteractionDBLoader':
        """Load from DrugBank XML (simplified)."""
        # This would parse DrugBank XML - simplified version
        logger.info("DrugBank loading not implemented in this version")
        return self
    
    def build_index(self, output_path: Optional[Path] = None):
        """Build and save search index."""
        index = {
            'interactions': self.interactions,
            'drugs': list(self.drugs)
        }
        
        if output_path:
            with open(output_path, 'wb') as f:
                pickle.dump(index, f)
            logger.info(f"Index saved to {output_path}")
        
        return index
    
    def load_index(self, index_path: Path) -> 'InteractionDBLoader':
        """Load pre-built index."""
        with open(index_path, 'rb') as f:
            index = pickle.load(f)
        
        self.interactions = index.get('interactions', {})
        self.drugs = set(index.get('drugs', []))
        
        logger.info(f"Loaded index with {len(self.interactions)} interactions")
        return self
    
    def get_interaction(self, drug1: str, drug2: str) -> List[Dict]:
        """Get interactions between two drugs."""
        pair = tuple(sorted([drug1.lower(), drug2.lower()]))
        return self.interactions.get(pair, [])
    
    def has_interaction(self, drug1: str, drug2: str) -> bool:
        """Check if interaction exists."""
        return len(self.get_interaction(drug1, drug2)) > 0
    
    def get_all_interactions_for_drug(self, drug: str) -> Dict[str, List[Dict]]:
        """Get all interactions for a single drug."""
        drug = drug.lower()
        result = {}
        
        for pair, interactions in self.interactions.items():
            if drug in pair:
                other_drug = pair[0] if pair[1] == drug else pair[1]
                result[other_drug] = interactions
        
        return result


class SimpleInteractionDB:
    """Hard-coded common interactions for demo purposes."""
    
    # Common serious interactions
    INTERACTIONS = {
        ('warfarin', 'aspirin'): {
            'severity': 'major',
            'description': 'Increased bleeding risk',
            'recommendation': 'Monitor INR closely or avoid combination'
        },
        ('metformin', 'contrast dye'): {
            'severity': 'major',
            'description': 'Risk of lactic acidosis',
            'recommendation': 'Hold metformin 48 hours before/after contrast'
        },
        ('lisinopril', 'spironolactone'): {
            'severity': 'moderate',
            'description': 'Risk of high potassium',
            'recommendation': 'Monitor potassium levels'
        },
        ('simvastatin', 'clarithromycin'): {
            'severity': 'major',
            'description': 'Increased statin levels, risk of muscle damage',
            'recommendation': 'Use alternative antibiotic or hold statin'
        },
        ('amoxicillin', 'probenecid'): {
            'severity': 'minor',
            'description': 'Increased amoxicillin levels',
            'recommendation': 'Usually beneficial, no action needed'
        }
    }
    
    @classmethod
    def check(cls, drug1: str, drug2: str) -> Optional[Dict]:
        """Check interaction between two drugs."""
        pair = tuple(sorted([drug1.lower(), drug2.lower()]))
        return cls.INTERACTIONS.get(pair)
    
    @classmethod
    def check_list(cls, drugs: List[str]) -> List[Dict]:
        """Check all pairs in a list."""
        interactions = []
        for i, d1 in enumerate(drugs):
            for d2 in drugs[i+1:]:
                result = cls.check(d1, d2)
                if result:
                    interactions.append({
                        'drug1': d1,
                        'drug2': d2,
                        **result
                    })
        return interactions