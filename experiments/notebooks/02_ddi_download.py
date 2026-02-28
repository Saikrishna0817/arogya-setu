#!/usr/bin/env python
"""Download and process drug-drug interactions from OpenFDA."""

import requests
import csv
import re
import pickle
from pathlib import Path
from typing import Dict, List

OPENFDA_URL = "https://api.fda.gov/drug/label.json"

# Severity keywords for classification
SEVERITY_KEYWORDS = {
    'contraindicated': ['contraindicated', 'should not be used', 'fatal', 'life-threatening'],
    'major': ['serious', 'severe', 'significant', 'major interaction', 'avoid combination'],
    'moderate': ['monitor', 'caution', 'reduce dose', 'moderate interaction'],
    'minor': ['minor', 'mild', 'usually no adjustment needed']
}

def classify_severity(description: str) -> str:
    """Classify interaction severity from description text."""
    desc_lower = description.lower()
    
    for severity, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return severity
    
    return 'unknown'

def extract_interactions(drug_data: Dict) -> List[Dict]:
    """Extract interactions from drug label."""
    interactions = []
    
    drug_name = drug_data.get('openfda', {}).get('generic_name', ['Unknown'])[0]
    interaction_text = drug_data.get('drug_interactions', [''])[0]
    
    if not interaction_text:
        return interactions
    
    # Parse interaction text (simplified regex-based)
    # Look for patterns like "Drug A: description"
    pattern = r'([A-Za-z\s]+):\s*([^\.]+(?:\.[^\.]+){0,2})'
    matches = re.findall(pattern, interaction_text)
    
    for drug_b, description in matches:
        drug_b = drug_b.strip()
        description = description.strip()
        
        if len(drug_b) < 3 or len(description) < 10:
            continue
        
        severity = classify_severity(description)
        
        interactions.append({
            'drug_a': drug_name,
            'drug_b': drug_b,
            'severity': severity,
            'description': description,
            'raw_text': interaction_text[:500]  # Truncate for storage
        })
    
    return interactions

def fetch_and_process():
    """Fetch and process interaction data."""
    all_interactions = []
    
    # Fetch drug labels with interaction data
    params = {
        'limit': 100,
        'skip': 0
    }
    
    for skip in range(0, 5000, 100):  # Adjust range as needed
        params['skip'] = skip
        
        try:
            response = requests.get(OPENFDA_URL, params=params, timeout=30)
            data = response.json()
            
            for result in data.get('results', []):
                interactions = extract_interactions(result)
                all_interactions.extend(interactions)
            
            print(f"Processed {skip} records, found {len(all_interactions)} interactions")
            
        except Exception as e:
            print(f"Error at skip={skip}: {e}")
            continue
    
    return all_interactions

def save_interactions(interactions: List[Dict], output_dir: Path):
    """Save to CSV and pickle index."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    csv_path = output_dir / 'ddi_cleaned_full.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['drug_a', 'drug_b', 'severity', 'description', 'raw_text'])
        writer.writeheader()
        writer.writerows(interactions)
    
    # Build and save index
    index = {}
    for inter in interactions:
        pair = tuple(sorted([inter['drug_a'].lower(), inter['drug_b'].lower()]))
        if pair not in index:
            index[pair] = []
        index[pair].append(inter)
    
    pkl_path = output_dir / 'interaction_index.pkl'
    with open(pkl_path, 'wb') as f:
        pickle.dump(index, f)
    
    print(f"Saved {len(interactions)} interactions to {csv_path}")
    print(f"Saved index with {len(index)} pairs to {pkl_path}")

def main():
    """Main execution."""
    print("Fetching drug interactions from OpenFDA...")
    interactions = fetch_and_process()
    
    output_dir = Path('data/interactions')
    save_interactions(interactions, output_dir)

if __name__ == "__main__":
    main()