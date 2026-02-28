"""Load lab report samples and reference data."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabDatasetLoader:
    """Load lab report reference data."""
    
    def __init__(self, dataset_path: Path):
        self.dataset_path = Path(dataset_path)
        self.reference_ranges: Dict[str, Dict] = {}
        self.knowledge_base: Dict[str, str] = {}
    
    def load_reference_csv(self, filename: str = 'lab_reference.csv') -> Dict:
        """Load lab reference ranges."""
        csv_path = self.dataset_path / filename
        
        if not csv_path.exists():
            logger.warning(f"Lab reference file not found: {csv_path}")
            return {}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_name = row.get('test_name', '').strip()
                if test_name:
                    self.reference_ranges[test_name.lower()] = {
                        'test_name': test_name,
                        'unit': row.get('unit', ''),
                        'normal_low': self._parse_float(row.get('normal_low')),
                        'normal_high': self._parse_float(row.get('normal_high')),
                        'category': row.get('category', 'General')
                    }
        
        logger.info(f"Loaded {len(self.reference_ranges)} lab reference ranges")
        return self.reference_ranges
    
    def load_knowledge_base(self, folder_name: str = 'knowledge_base') -> Dict[str, str]:
        """Load knowledge base articles."""
        kb_path = self.dataset_path / folder_name
        
        if not kb_path.exists():
            logger.warning(f"Knowledge base folder not found: {kb_path}")
            return {}
        
        for file_path in kb_path.glob('*.md'):
            test_name = file_path.stem
            self.knowledge_base[test_name.lower()] = file_path.read_text(encoding='utf-8')
        
        logger.info(f"Loaded {len(self.knowledge_base)} knowledge base articles")
        return self.knowledge_base
    
    def get_reference_for_test(self, test_name: str) -> Optional[Dict]:
        """Get reference range for specific test."""
        return self.reference_ranges.get(test_name.lower())
    
    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        """Safely parse float."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None