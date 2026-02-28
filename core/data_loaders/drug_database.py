"""Load and integrate drug databases."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrugDatabaseLoader:
    """Load custom drug databases."""
    
    def __init__(self, csv_path: Optional[Path] = None):
        self.drugs: List[Dict] = []
        self.interactions: List[Dict] = []
        
        if csv_path and csv_path.exists():
            self.load_from_csv(csv_path)
    
    def load_from_csv(self, csv_path: Path, delimiter: str = ',') -> 'DrugDatabaseLoader':
        """Load drug database from CSV."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                self.drugs.append({
                    'brand_name': row.get('brand_name', '').strip(),
                    'generic_name': row.get('generic_name', '').strip(),
                    'category': row.get('category', 'unknown'),
                    'common_doses': row.get('common_doses', ''),
                    'unit': row.get('unit', 'mg'),
                    'max_daily_dose': self._parse_float(row.get('max_daily_dose')),
                    'source': 'user_dataset'
                })
        
        logger.info(f"Loaded {len(self.drugs)} drugs from {csv_path}")
        return self
    
    def load_interactions(self, csv_path: Path) -> 'DrugDatabaseLoader':
        """Load drug interactions from CSV."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.interactions.append({
                    'drug1': row.get('drug1', '').lower().strip(),
                    'drug2': row.get('drug2', '').lower().strip(),
                    'severity': row.get('severity', 'unknown').lower(),
                    'description': row.get('description', ''),
                    'source': 'user_dataset'
                })
        
        logger.info(f"Loaded {len(self.interactions)} interactions from {csv_path}")
        return self
    
    def get_interaction_index(self) -> Dict:
        """Build interaction lookup index."""
        index = {}
        
        for inter in self.interactions:
            pair = tuple(sorted([inter['drug1'], inter['drug2']]))
            if pair not in index:
                index[pair] = []
            index[pair].append(inter)
        
        return index
    
    def export_for_app(self, output_path: Path):
        """Export merged database for app use."""
        interactions = self.get_interaction_index()
        
        export_data = {
            'drugs': {d['generic_name'].lower(): d for d in self.drugs if d.get('generic_name')},
            'interactions': interactions,
            'metadata': {
                'drug_count': len(self.drugs),
                'interaction_count': len(interactions)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported database to {output_path}")
    
    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        """Safely parse float from string."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None