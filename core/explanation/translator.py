"""Translation service with medical term handling."""

from typing import Optional
import logging
from googletrans import Translator as GoogleTranslator
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import re

from config.languages import LANG_CONFIG, MEDICAL_TERMS
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Translator:
    """Multi-language translator optimized for medical content."""
    
    def __init__(self, use_local: bool = False):
        self.use_local = use_local
        self.google_trans = GoogleTranslator()
        
        # Load local model if requested (better quality, no API limits)
        self.local_model = None
        self.local_tokenizer = None
        
        if use_local:
            self._load_local_model()
    
    def _load_local_model(self):
        """Load AI4Bharat IndicTrans2 for high-quality translation."""
        try:
            model_name = "ai4bharat/indictrans2-en-indic-1B"
            self.local_tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
            self.local_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            logger.info("Loaded local translation model")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self.use_local = False
    
    def translate(self, text: str, target_lang: str, 
                  preserve_medical: bool = True) -> str:
        """
        Translate text to target language.
        
        Args:
            text: English text to translate
            target_lang: Target language code ('hi', 'te', etc.)
            preserve_medical: Keep medical terms in English with translation in parentheses
            
        Returns:
            Translated text
        """
        if target_lang == 'en' or not text:
            return text
        
        # Step 1: Protect medical terms if requested
        protected_terms = {}
        if preserve_medical:
            text, protected_terms = self._protect_medical_terms(text)
        
        # Step 2: Translate
        if self.use_local and self.local_model and target_lang in ['hi', 'te', 'ta', 'mr', 'bn']:
            translated = self._translate_local(text, target_lang)
        else:
            translated = self._translate_google(text, target_lang)
        
        # Step 3: Restore medical terms with translations
        if preserve_medical:
            translated = self._restore_medical_terms(translated, protected_terms, target_lang)
        
        return translated
    
    def _protect_medical_terms(self, text: str) -> tuple:
        """Replace medical terms with placeholders."""
        protected = {}
        counter = 0
        
        # Protect frequency codes
        for code in MEDICAL_TERMS.keys():
            pattern = r'\b' + re.escape(code) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                placeholder = f"__MED{counter}__"
                protected[placeholder] = code
                text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)
                counter += 1
        
        # Protect drug names (simple heuristic - capitalized words)
        drug_pattern = r'\b([A-Z][a-zA-Z]{2,}(?:\s+\d+)?)\b'
        for match in re.finditer(drug_pattern, text):
            drug = match.group(1)
            if len(drug) > 3:  # Avoid protecting common words
                placeholder = f"__MED{counter}__"
                protected[placeholder] = drug
                text = text.replace(drug, placeholder, 1)
                counter += 1
        
        return text, protected
    
    def _restore_medical_terms(self, text: str, protected: dict, 
                               target_lang: str) -> str:
        """Restore medical terms with translations."""
        for placeholder, original in protected.items():
            # Get translation of term
            if original in MEDICAL_TERMS and target_lang in MEDICAL_TERMS[original]:
                translation = MEDICAL_TERMS[original][target_lang]
                replacement = f"{original} ({translation})"
            else:
                # Try to translate the term itself
                try:
                    term_trans = self._translate_google(original, target_lang)
                    replacement = f"{original} ({term_trans})"
                except:
                    replacement = original
            
            text = text.replace(placeholder, replacement, 1)
        
        return text
    
    def _translate_google(self, text: str, target_lang: str) -> str:
        """Google Translate fallback."""
        try:
            # Map language codes
            lang_map = {'te': 'te', 'hi': 'hi', 'ta': 'ta', 'en': 'en'}
            dest = lang_map.get(target_lang, target_lang)
            
            result = self.google_trans.translate(text, dest=dest, src='en')
            return result.text
        except Exception as e:
            logger.error(f"Google translation failed: {e}")
            return text  # Return original on failure
    
    def _translate_local(self, text: str, target_lang: str) -> str:
        """Use local IndicTrans2 model."""
        if not self.local_model:
            return self._translate_google(text, target_lang)
        
        # Language code mapping
        lang_codes = {
            'hi': 'hin_Deva',
            'te': 'tel_Telu',
            'ta': 'tam_Taml',
            'bn': 'ben_Beng',
            'mr': 'mar_Deva'
        }
        
        tgt_code = lang_codes.get(target_lang, 'hin_Deva')
        
        # Prepare input
        inputs = self.local_tokenizer(
            f"eng_Latn {text}",
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Generate
        with torch.no_grad():
            outputs = self.local_model.generate(
                **inputs,
                forced_bos_token_id=self.local_tokenizer.lang_code_to_id[tgt_code],
                max_length=512
            )
        
        translated = self.local_tokenizer.batch_decode(
            outputs, skip_special_tokens=True
        )[0]
        
        return translated
    
    def translate_prescription_explanation(self, explanation: str, 
                                          target_lang: str) -> str:
        """Special handling for prescription explanations."""
        # Add context for better translation
        context = "Medical prescription explanation for patient: "
        full_text = context + explanation
        
        translated = self.translate(full_text, target_lang)
        
        # Remove context prefix if present
        for prefix in ["Medical prescription explanation for patient:", 
                      "मरीज के लिए मेडिकल प्रिस्क्रिप्शन व्याख्या:",
                      "రోగికి వైద్య నిర్దేశం వివరణ:"]:
            if translated.startswith(prefix):
                translated = translated[len(prefix):].strip()
        
        return translated