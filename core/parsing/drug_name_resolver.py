"""Resolve drug names using fuzzy matching against OpenFDA database."""

import csv
import json
from pathlib import Path
from typing import Dict, Optional, List
from rapidfuzz import fuzz, process
import logging

from config.dosage_limits import BRAND_TO_GENERIC, DOSAGE_LIMITS
from config.paths import Paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrugNameResolver:
    """Fuzzy matching for drug names using OpenFDA data."""
    
    def __init__(self, drug_list_path: Optional[Path] = None):
        self.drugs: List[Dict] = []
        self.name_index: Dict[str, Dict] = {}  # name -> drug info
        self.aliases: Dict[str, str] = {}  # alias -> generic
        
        # Load built-in data first
        self._load_builtin()
        
        # Load OpenFDA data if available
        openfda_path = Paths.DRUG_LIST / 'drugs.csv'
        aliases_path = Paths.DRUG_LIST / 'drug_aliases.csv'
        
        if openfda_path.exists():
            self._load_openfda(openfda_path, aliases_path)
        elif drug_list_path and drug_list_path.exists():
            self._load_csv(drug_list_path)
        
        # Build search index
        self.all_names = list(self.name_index.keys())
        logger.info(f"Loaded {len(self.drugs)} drugs, {len(self.all_names)} names, {len(self.aliases)} aliases")
    
    def _load_builtin(self):
        """Load from dosage limits and brand mappings."""
        # From DOSAGE_LIMITS (generic names)
        for generic_name in DOSAGE_LIMITS.keys():
            entry = {
                'generic': generic_name,
                'brand': None,
                'aliases': [],
                'category': self._categorize(generic_name),
                'source': 'builtin'
            }
            self.drugs.append(entry)
            self.name_index[generic_name.lower()] = entry
            
            # Add common variations
            self.name_index[generic_name.lower().replace(' ', '')] = entry
        
        # From BRAND_TO_GENERIC
        for brand, generic in BRAND_TO_GENERIC.items():
            entry = self.name_index.get(generic.lower(), {
                'generic': generic,
                'brand': brand,
                'aliases': [],
                'category': 'unknown',
                'source': 'builtin_brand'
            })
            entry['brand'] = brand
            self.name_index[brand.lower()] = entry
    
    def _load_openfda(self, drugs_path: Path, aliases_path: Path):
        """Load OpenFDA drug database."""
        logger.info(f"Loading OpenFDA data from {drugs_path}")
        
        # Load main drug list
        with open(drugs_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                generic = row.get('generic_name', '').strip()
                brands = row.get('brand_names', '').split('|')
                substances = row.get('substance', '').split('|')
                drug_class = row.get('drug_class', 'unknown')
                
                if not generic or generic == 'Unknown':
                    continue
                
                entry = {
                    'generic': generic,
                    'brand': brands[0] if brands and brands[0] else None,
                    'all_brands': [b for b in brands if b],
                    'substances': [s for s in substances if s],
                    'category': drug_class,
                    'source': 'openfda'
                }
                
                self.drugs.append(entry)
                
                # Index by generic name
                self.name_index[generic.lower()] = entry
                
                # Index by all brand names
                for brand in brands:
                    if brand:
                        self.name_index[brand.lower()] = entry
                        self.aliases[brand.lower()] = generic
        
        # Load explicit aliases
        if aliases_path.exists():
            with open(aliases_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    alias = row.get('alias', '').strip().lower()
                    generic = row.get('generic_name', '').strip()
                    if alias and generic:
                        self.aliases[alias] = generic
                        if alias not in self.name_index:
                            self.name_index[alias] = {
                                'generic': generic,
                                'alias_type': row.get('type', 'unknown'),
                                'source': 'openfda_alias'
                            }
    
    def _load_csv(self, path: Path):
        """Load from custom CSV."""
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.drugs.append(row)
                for key in ['generic', 'brand', 'name', 'alias']:
                    if key in row and row[key]:
                        self.name_index[row[key].lower()] = row
    
    def _categorize(self, drug_name: str) -> str:
        """Simple categorization."""
        categories = {
            'cardiac': ['Amlodipine', 'Metoprolol', 'Losartan', 'Telmisartan', 'Atenolol'],
            'diabetes': ['Metformin', 'Glimepiride', 'Insulin', 'Gliclazide'],
            'pain': ['Paracetamol', 'Ibuprofen', 'Diclofenac', 'Tramadol'],
            'antibiotic': ['Amoxicillin', 'Azithromycin', 'Ciprofloxacin', 'Cefixime'],
            'gi': ['Omeprazole', 'Pantoprazole', 'Ranitidine', 'Ondansetron'],
            'vitamin': ['Vitamin', 'Calcium', 'Iron', 'Folic Acid']
        }
        
        for cat, drugs in categories.items():
            if any(d.lower() in drug_name.lower() for d in drugs):
                return cat
        return 'other'
    
    def resolve(self, name: str, threshold: int = 70) -> Optional[Dict]:
        """
        Resolve drug name with fuzzy matching.
        
        Args:
            name: Input drug name (possibly misspelled)
            threshold: Minimum match score (0-100)
            
        Returns:
            Resolved drug info or None
        """
        if not name or len(name) < 2:
            return None
        
        name_clean = name.lower().strip()
        
        # Check aliases first
        if name_clean in self.aliases:
            generic = self.aliases[name_clean]
            return {
                'generic': generic,
                'brand': name_clean if name_clean != generic.lower() else None,
                'category': self.name_index.get(generic.lower(), {}).get('category', 'unknown'),
                'confidence': 1.0,
                'match_type': 'alias'
            }
        
        # Exact match
        if name_clean in self.name_index:
            result = self.name_index[name_clean]
            return {
                'generic': result.get('generic'),
                'brand': result.get('brand'),
                'category': result.get('category', 'unknown'),
                'confidence': 1.0,
                'match_type': 'exact'
            }
        
        # Fuzzy match
        matches = process.extract(name_clean, self.all_names, scorer=fuzz.token_sort_ratio, limit=3)
        
        if matches and matches[0][1] >= threshold:
            best_match = matches[0][0]
            result = self.name_index[best_match]
            
            return {
                'generic': result.get('generic'),
                'brand': result.get('brand'),
                'category': result.get('category', 'unknown'),
                'confidence': matches[0][1] / 100.0,
                'match_type': 'fuzzy',
                'alternatives': [(m[0], m[1]) for m in matches[1:]]
            }
        
        # No good match
        return {
            'generic': None,
            'brand': None,
            'category': 'unknown',
            'confidence': 0.0,
            'match_type': 'none'
        }
    
    def get_dosage_info(self, generic_name: str) -> Optional[Dict]:
        """Get dosage limits for generic name."""
        return DOSAGE_LIMITS.get(generic_name)
    
    def suggest_corrections(self, name: str, limit: int = 3) -> List[str]:
        """Suggest similar drug names."""
        matches = process.extract(name.lower(), self.all_names, scorer=fuzz.token_sort_ratio, limit=limit)
        return [m[0] for m in matches if m[1] > 50]
    
    def search_by_class(self, drug_class: str) -> List[Dict]:
        """Find all drugs in a therapeutic class."""
        results = []
        for drug in self.drugs:
            if drug.get('category', '').lower() == drug_class.lower():
                results.append(drug)
        return results