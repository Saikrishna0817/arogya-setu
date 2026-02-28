"""Load and manage drug interaction databases."""

import csv
import json
import pickle
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

from config.paths import Paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionDBLoader:
    """Load DrugBank, OpenFDA, or custom interaction data."""
    
    def __init__(self):
        self.interactions: Dict[str, List[Dict]] = {}  # drug_pair -> interactions
        self.drugs: Set[str] = set()
        self.severity_stats = {'contraindicated': 0, 'major': 0, 'moderate': 0, 'minor': 0, 'unknown': 0}
    
    def load_from_csv(self, csv_path: Path) -> 'InteractionDBLoader':
        """Load cleaned interaction CSV from OpenFDA."""
        if not csv_path.exists():
            logger.warning(f"Interaction CSV not found: {csv_path}")
            return self
        
        logger.info(f"Loading interactions from {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                drug1 = row.get('drug_a', '').lower().strip()
                drug2 = row.get('drug_b', '').lower().strip()
                
                if not drug1 or not drug2:
                    continue
                
                pair = tuple(sorted([drug1, drug2]))
                
                interaction = {
                    'drug_a': drug1,
                    'drug_b': drug2,
                    'severity': row.get('severity', 'unknown').lower(),
                    'description': row.get('description', ''),
                    'source': 'openfda'
                }
                
                if pair not in self.interactions:
                    self.interactions[pair] = []
                self.interactions[pair].append(interaction)
                
                self.drugs.add(drug1)
                self.drugs.add(drug2)
                
                # Track severity stats
                sev = interaction['severity']
                if sev in self.severity_stats:
                    self.severity_stats[sev] += 1
        
        logger.info(f"Loaded {len(self.interactions)} interaction pairs")
        logger.info(f"Severity distribution: {self.severity_stats}")
        return self
    
    def load_index(self, index_path: Path) -> 'InteractionDBLoader':
        """Load pre-built pickle index."""
        if not index_path.exists():
            logger.warning(f"Index not found: {index_path}")
            return self
        
        with open(index_path, 'rb') as f:
            index = pickle.load(f)
        
        self.interactions = index
        self.drugs = set()
        for pair in self.interactions.keys():
            self.drugs.update(pair)
        
        logger.info(f"Loaded index with {len(self.interactions)} pairs")
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
    
    def get_severity_stats(self) -> Dict[str, int]:
        """Get statistics on interaction severities."""
        return self.severity_stats


class SimpleInteractionDB:
    """Fallback for common interactions if OpenFDA data not available."""
    
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