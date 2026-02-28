#!/usr/bin/env python
"""Download and process OpenFDA drug data."""

import requests
import json
import csv
import time
from pathlib import Path
from typing import List, Dict

# API Configuration
OPENFDA_URL = "https://api.fda.gov/drug/label.json"
BATCH_SIZE = 100
MAX_RECORDS = 10000  # Adjust as needed

def fetch_openfda_drugs():
    """Fetch drug data from OpenFDA API."""
    all_drugs = []
    skip = 0
    
    while skip < MAX_RECORDS:
        params = {
            'limit': BATCH_SIZE,
            'skip': skip
        }
        
        try:
            response = requests.get(OPENFDA_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:
                break
                
            all_drugs.extend(results)
            print(f"Fetched {len(all_drugs)} records...")
            
            skip += BATCH_SIZE
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Error at skip={skip}: {e}")
            break
    
    return all_drugs

def process_drugs(raw_data: List[Dict]):
    """Process raw API data into clean format."""
    drugs = []
    aliases = []
    
    for item in raw_data:
        # Extract generic name
        generic = item.get('openfda', {}).get('generic_name', ['Unknown'])[0]
        
        # Extract brand names
        brands = item.get('openfda', {}).get('brand_name', [])
        
        # Extract substance
        substances = item.get('openfda', {}).get('substance_name', [])
        
        # Extract pharmacological class
        drug_class = item.get('openfda', {}).get('pharmacological_class', ['Unknown'])[0]
        
        drug_record = {
            'generic_name': generic,
            'brand_names': '|'.join(brands),
            'substance': '|'.join(substances),
            'drug_class': drug_class,
            'product_type': item.get('openfda', {}).get('product_type', [''])[0]
        }
        drugs.append(drug_record)
        
        # Create alias mappings
        for brand in brands:
            aliases.append({
                'alias': brand,
                'generic_name': generic,
                'type': 'brand_name'
            })
        
        for substance in substances:
            aliases.append({
                'alias': substance,
                'generic_name': generic,
                'type': 'substance'
            })
    
    return drugs, aliases

def save_to_csv(drugs: List[Dict], aliases: List[Dict], output_dir: Path):
    """Save processed data to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save drugs
    drugs_file = output_dir / 'drugs.csv'
    with open(drugs_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['generic_name', 'brand_names', 'substance', 'drug_class', 'product_type'])
        writer.writeheader()
        writer.writerows(drugs)
    
    # Save aliases
    aliases_file = output_dir / 'drug_aliases.csv'
    with open(aliases_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['alias', 'generic_name', 'type'])
        writer.writeheader()
        writer.writerows(aliases)
    
    # Save raw JSON for reference
    raw_file = output_dir / 'raw_fda_drugs.json'
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump({'drugs': drugs, 'aliases': aliases}, f, indent=2)
    
    print(f"Saved {len(drugs)} drugs to {drugs_file}")
    print(f"Saved {len(aliases)} aliases to {aliases_file}")

def main():
    """Main execution."""
    print("Fetching OpenFDA drug data...")
    raw_data = fetch_openfda_drugs()
    
    print("Processing data...")
    drugs, aliases = process_drugs(raw_data)
    
    output_dir = Path('data/drug_list')
    save_to_csv(drugs, aliases, output_dir)
    
    print("Done!")

if __name__ == "__main__":
    main()