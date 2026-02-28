from pathlib import Path

class Paths:
    # Base directory (project root)
    _UTILS_DIR = Path(__file__).parent.resolve()
    BASE_DIR = _UTILS_DIR.parent.resolve()
    
    # DATA DIRECTORIES (THESE WERE MISSING!)
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    INTERACTIONS_DIR = DATA_DIR / 'interactions'
    
    # Specific file paths
    DDI_CLEANED_FULL = INTERACTIONS_DIR / 'ddi_cleaned_full.csv'