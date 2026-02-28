#!/usr/bin/env python
"""Build drug interaction index."""

import csv
import pickle
from pathlib import Path
from config.paths import Paths
from core.interaction.interaction_db_loader import InteractionDBLoader


def main():
    """Build interaction index from CSV."""
    loader = InteractionDBLoader()
    
    # Load from CSV if exists
    csv_path = Paths.DATA_DIR / 'interactions' / 'ddi_cleaned.csv'
    if csv_path.exists():
        loader.load_from_csv(csv_path)
        print(f"Loaded {len(loader.interactions)} interactions from CSV")
    else:
        print("No CSV found, using built-in interactions")
    
    # Build and save index
    index_path = Paths.DATA_DIR / 'interactions' / 'interaction_index.pkl'
    loader.build_index(index_path)
    print(f"Index saved to {index_path}")


if __name__ == "__main__":
    main()