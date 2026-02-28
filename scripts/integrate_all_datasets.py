"""
VERNACULAR Dataset Integration Script

This script integrates multiple data sources for the VERNACULAR project:
- Drug data (drugs.csv)
- Drug-Drug Interaction data (DDI)
- Dosage data (safe doses, pediatric, renal adjustments)
- Lab reference data
- Prescription images and annotations
- Vault database

Usage:
    python scripts/integrate_all_datasets.py

Prerequisites:
    - Ensure config/paths.py exists with all required Path attributes
    - Run data preparation scripts if data files are missing
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config.paths import Paths
except ImportError as e:
    print(f"ERROR: Could not import Paths from config.paths: {e}")
    print("\nMake sure config/paths.py exists and contains the Paths class.")
    print("Expected structure:")
    print("  VERNACULAR/")
    print("    ├── config/")
    print("    │   ├── __init__.py")
    print("    │   └── paths.py")
    print("    └── scripts/")
    print("        └── integrate_all_datasets.py")
    sys.exit(1)


def integrate_drug_data():
    """Integrate drug data from various sources."""
    print("\n" + "=" * 60)
    print("INTEGRATING DRUG DATA")
    print("=" * 60)
    
    # Check for main drug data file
    if Paths.DRUGS_CSV.exists():
        print(f"Found drug data: {Paths.DRUGS_CSV}")
        try:
            import pandas as pd
            df = pd.read_csv(Paths.DRUGS_CSV)
            print(f"  - {len(df)} drugs loaded")
        except Exception as e:
            print(f"  - Warning: Could not read CSV: {e}")
    else:
        print(f"Drug data not found: {Paths.DRUGS_CSV}")
        print("  Run: python experiments/notebooks/01_data_preparation.py")

    # Check for DDI (Drug-Drug Interaction) data
    if Paths.DDI_CLEANED_FULL_CSV.exists():
        print(f"Found DDI data: {Paths.DDI_CLEANED_FULL_CSV}")
        try:
            import pandas as pd
            df = pd.read_csv(Paths.DDI_CLEANED_FULL_CSV)
            print(f"  - {len(df)} interactions loaded")
        except Exception as e:
            print(f"  - Warning: Could not read CSV: {e}")
    else:
        print(f"DDI data not found: {Paths.DDI_CLEANED_FULL_CSV}")
        print("  Run: python experiments/notebooks/02_ddi_download.py")


def integrate_dosage_data():
    """Integrate dosage-related data files."""
    print("\n" + "=" * 60)
    print("INTEGRATING DOSAGE DATA")
    print("=" * 60)
    
    files = {
        'Safe doses': Paths.SAFE_DOSE_CSV,
        'Pediatric': Paths.PEDIATRIC_DOSE_CSV,
        'Renal': Paths.RENAL_ADJUST_CSV,
    }
    
    found_count = 0
    for name, path in files.items():
        if path.exists():
            print(f"Found {name}: {path}")
            found_count += 1
        else:
            print(f"{name}: Not found (using built-in defaults)")
    
    if found_count == 0:
        print("  Note: No dosage files found. Built-in defaults will be used.")


def integrate_lab_data():
    """Integrate laboratory reference data."""
    print("\n" + "=" * 60)
    print("INTEGRATING LAB DATA")
    print("=" * 60)
    
    # Check for lab reference CSV
    if Paths.LAB_REFERENCE_CSV.exists():
        print(f"Lab reference: {Paths.LAB_REFERENCE_CSV}")
        try:
            import pandas as pd
            df = pd.read_csv(Paths.LAB_REFERENCE_CSV)
            print(f"  - {len(df)} lab tests loaded")
        except Exception as e:
            print(f"  - Warning: Could not read CSV: {e}")
    else:
        print(f"Lab reference CSV not found: {Paths.LAB_REFERENCE_CSV}")

    # Check for knowledge base directory
    if Paths.LAB_KB_DIR.exists():
        md_files = list(Paths.LAB_KB_DIR.glob('*.md'))
        print(f"Knowledge base: {len(md_files)} articles in {Paths.LAB_KB_DIR}")
    else:
        print(f"Knowledge base not found: {Paths.LAB_KB_DIR}")


def integrate_prescription_images():
    """Integrate prescription image data and annotations."""
    print("\n" + "=" * 60)
    print("INTEGRATING PRESCRIPTION IMAGES")
    print("=" * 60)
    
    # Check for raw images
    if Paths.PRESCRIPTIONS_RAW.exists():
        jpg_count = len(list(Paths.PRESCRIPTIONS_RAW.glob('*.jpg')))
        png_count = len(list(Paths.PRESCRIPTIONS_RAW.glob('*.png')))
        jpeg_count = len(list(Paths.PRESCRIPTIONS_RAW.glob('*.jpeg')))
        total = jpg_count + png_count + jpeg_count
        print(f"Raw images: {total} in {Paths.PRESCRIPTIONS_RAW}")
        if total > 0:
            print(f"  - {jpg_count} JPG, {png_count} PNG, {jpeg_count} JPEG")
    else:
        print(f"Raw images directory not found: {Paths.PRESCRIPTIONS_RAW}")

    # Check for annotations
    if Paths.PRESCRIPTIONS_ANNOTATIONS.exists():
        ann_count = len(list(Paths.PRESCRIPTIONS_ANNOTATIONS.glob('*.json')))
        print(f"Annotations: {ann_count} in {Paths.PRESCRIPTIONS_ANNOTATIONS}")
    else:
        print(f"Annotations directory not found: {Paths.PRESCRIPTIONS_ANNOTATIONS}")


def integrate_vault():
    """Integrate the vault SQLite database."""
    print("\n" + "=" * 60)
    print("INTEGRATING VAULT DATABASE")
    print("=" * 60)
    
    if Paths.VAULT_DB.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(Paths.VAULT_DB)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                print(f"Vault database: {Paths.VAULT_DB}")
                print(f"  Tables found: {', '.join(tables)}")
                
                # Check for expected tables
                expected_tables = ['prescriptions', 'patients', 'drugs', 'interactions']
                for table in expected_tables:
                    if table in tables:
                        try:
                            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                            print(f"  - {table}: {count} records")
                        except Exception as e:
                            print(f"  - {table}: error reading - {e}")
            else:
                print(f"Vault database exists but has no tables: {Paths.VAULT_DB}")
            
            conn.close()
        except Exception as e:
            print(f"Error reading vault database: {e}")
    else:
        print(f"Vault database not found: {Paths.VAULT_DB}")
        print("  Run: python scripts/init_database.py")


def print_summary():
    """Print a summary of the integration check."""
    print("\n" + "=" * 60)
    print("INTEGRATION CHECK COMPLETE")
    print("=" * 60)
    print("All 'not found' items are expected at this stage — data not downloaded yet.")
    print()
    print("Next steps:")
    print("  1. Run data preparation notebooks in experiments/notebooks/")
    print("  2. Download required datasets")
    print("  3. Re-run this script to verify")
    print("=" * 60)


def main():
    """Main integration workflow."""
    print("VERNACULAR DATASET INTEGRATION")
    print("Checking all configured datasets...")
    
    # Ensure all directories exist
    try:
        Paths.ensure_all_dirs()
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")
    
    # Run all integration checks
    integrate_drug_data()
    integrate_dosage_data()
    integrate_lab_data()
    integrate_prescription_images()
    integrate_vault()
    
    # Print final summary
    print_summary()


if __name__ == "__main__":
    main()