"""
Path configuration for VERNACULAR project.
All directory and file paths are centralized here for easy maintenance.
"""
from pathlib import Path


class Paths:
    """
    Centralized path management for the VERNACULAR project.
    
    Usage:
        from config.paths import Paths
        
        # Access directories
        data_path = Paths.DATA_DIR
        drugs_file = Paths.DRUGS_CSV
    """
    
    # ========================================================================
    # BASE DIRECTORY
    # ========================================================================
    # Get the directory where this file is located (config/)
    _CONFIG_DIR = Path(__file__).parent.resolve()
    
    # Project root is one level up from config/
    BASE_DIR = _CONFIG_DIR.parent.resolve()
    
    # ========================================================================
    # DATA DIRECTORIES
    # ========================================================================
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    INTERACTIONS_DIR = DATA_DIR / 'interactions'
    DOSAGE_DIR = DATA_DIR / 'dosage'
    LAB_DIR = DATA_DIR / 'lab'
    VAULT_DIR = DATA_DIR / 'vault'
    
    # ========================================================================
    # PRESCRIPTION DATA
    # ========================================================================
    PRESCRIPTIONS_DIR = DATA_DIR / 'prescriptions'
    PRESCRIPTIONS_RAW = PRESCRIPTIONS_DIR / 'raw'
    PRESCRIPTIONS_PROCESSED = PRESCRIPTIONS_DIR / 'processed'
    PRESCRIPTIONS_ANNOTATIONS = PRESCRIPTIONS_DIR / 'annotations'
    
    # ========================================================================
    # KNOWLEDGE BASE
    # ========================================================================
    KB_DIR = BASE_DIR / 'knowledge_base'
    LAB_KB_DIR = KB_DIR / 'lab'
    
    # ========================================================================
    # EXPERIMENT DIRECTORIES
    # ========================================================================
    EXPERIMENTS_DIR = BASE_DIR / 'experiments'
    NOTEBOOKS_DIR = EXPERIMENTS_DIR / 'notebooks'
    RESULTS_DIR = EXPERIMENTS_DIR / 'results'
    
    # ========================================================================
    # SCRIPTS & CONFIG
    # ========================================================================
    SCRIPTS_DIR = BASE_DIR / 'scripts'
    CONFIG_DIR = BASE_DIR / 'config'
    
    # ========================================================================
    # DRUG DATA FILES
    # ========================================================================
    DRUGS_CSV = DATA_DIR / 'drugs.csv'
    DRUGS_JSON = DATA_DIR / 'drugs.json'
    
    # ========================================================================
    # DRUG-DRUG INTERACTION (DDI) FILES
    # ========================================================================
    DDI_CLEANED_FULL_CSV = INTERACTIONS_DIR / 'ddi_cleaned_full.csv'
    DDI_MAPPED_CSV = INTERACTIONS_DIR / 'ddi_mapped.csv'
    DDI_JSON = INTERACTIONS_DIR / 'ddi.json'
    
    # ========================================================================
    # DOSAGE DATA FILES
    # ========================================================================
    SAFE_DOSE_CSV = DOSAGE_DIR / 'safe_doses.csv'
    PEDIATRIC_DOSE_CSV = DOSAGE_DIR / 'pediatric_doses.csv'
    RENAL_ADJUST_CSV = DOSAGE_DIR / 'renal_adjustments.csv'
    HEPATIC_ADJUST_CSV = DOSAGE_DIR / 'hepatic_adjustments.csv'
    
    # ========================================================================
    # LAB DATA FILES
    # ========================================================================
    LAB_REFERENCE_CSV = LAB_DIR / 'lab_reference.csv'
    LAB_RANGES_JSON = LAB_DIR / 'lab_ranges.json'
    
    # ========================================================================
    # VAULT DATABASE
    # ========================================================================
    VAULT_DB = VAULT_DIR / 'vault.db'
    VAULT_SCHEMA = VAULT_DIR / 'schema.sql'
    
    # ========================================================================
    # OPENFDA DATA (if used)
    # ========================================================================
    OPENFDA_DIR = RAW_DATA_DIR / 'openfda'
    OPENFDA_DRUGS = OPENFDA_DIR / 'drugs.json'
    OPENFDA_LABELS = OPENFDA_DIR / 'labels.json'
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    @classmethod
    def ensure_all_dirs(cls):
        """Create all data directories if they don't exist."""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.INTERACTIONS_DIR,
            cls.DOSAGE_DIR,
            cls.LAB_DIR,
            cls.VAULT_DIR,
            cls.PRESCRIPTIONS_DIR,
            cls.PRESCRIPTIONS_RAW,
            cls.PRESCRIPTIONS_PROCESSED,
            cls.PRESCRIPTIONS_ANNOTATIONS,
            cls.KB_DIR,
            cls.LAB_KB_DIR,
            cls.EXPERIMENTS_DIR,
            cls.NOTEBOOKS_DIR,
            cls.RESULTS_DIR,
            cls.OPENFDA_DIR,
        ]
        
        created_count = 0
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                created_count += 1
        
        if created_count > 0:
            print(f"Created {created_count} directories")
        else:
            print("All directories already exist")
    
    @classmethod
    def print_structure(cls):
        """Print the current path configuration for debugging."""
        print("VERNACULAR Project Paths:")
        print(f"  BASE_DIR: {cls.BASE_DIR}")
        print(f"  DATA_DIR: {cls.DATA_DIR}")
        print(f"  RAW_DATA_DIR: {cls.RAW_DATA_DIR}")
        print(f"  PROCESSED_DATA_DIR: {cls.PROCESSED_DATA_DIR}")
        print(f"  INTERACTIONS_DIR: {cls.INTERACTIONS_DIR}")
        print(f"  DOSAGE_DIR: {cls.DOSAGE_DIR}")
        print(f"  LAB_DIR: {cls.LAB_DIR}")
        print(f"  VAULT_DIR: {cls.VAULT_DIR}")
        print(f"  PRESCRIPTIONS_DIR: {cls.PRESCRIPTIONS_DIR}")
        print(f"  KB_DIR: {cls.KB_DIR}")
        print()
        print("Key Files:")
        print(f"  DRUGS_CSV: {cls.DRUGS_CSV}")
        print(f"  DDI_CLEANED_FULL_CSV: {cls.DDI_CLEANED_FULL_CSV}")
        print(f"  SAFE_DOSE_CSV: {cls.SAFE_DOSE_CSV}")
        print(f"  LAB_REFERENCE_CSV: {cls.LAB_REFERENCE_CSV}")
        print(f"  VAULT_DB: {cls.VAULT_DB}")