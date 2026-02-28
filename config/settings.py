"""Centralized application settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration."""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = Path(os.getenv('DATA_DIR', BASE_DIR / 'data'))
    MODELS_DIR = Path(os.getenv('MODELS_DIR', BASE_DIR / 'models'))
    
    # Tesseract
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    
    # Feature Flags
    USE_LOCAL_LLM = os.getenv('USE_LOCAL_LLM', 'true').lower() == 'true'
    USE_GOOGLE_CLOUD_TTS = os.getenv('USE_GOOGLE_CLOUD_TTS', 'false').lower() == 'true'
    ENABLE_ENCRYPTION = os.getenv('ENABLE_ENCRYPTION', 'true').lower() == 'true'
    
    # LLM Settings
    LOCAL_LLM_MODEL = "microsoft/DialoGPT-medium"  # Fallback, can upgrade to Zephyr/Mistral
    GEMINI_MODEL = "gemini-pro"
    
    # Safety
    MAX_DOSAGE_MULTIPLIER = 2.0  # Flag if exceeds 2x standard dose
    MIN_CONFIDENCE_THRESHOLD = 0.6
    
    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories."""
        dirs = [
            cls.DATA_DIR / 'prescriptions' / 'raw',
            cls.DATA_DIR / 'prescriptions' / 'clean',
            cls.DATA_DIR / 'prescriptions' / 'annotations',
            cls.DATA_DIR / 'lab_reports' / 'raw',
            cls.DATA_DIR / 'vault',
            cls.MODELS_DIR / 'ocr',
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)