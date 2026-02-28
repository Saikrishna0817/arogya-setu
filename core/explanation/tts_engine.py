"""Text-to-Speech engine with multiple voice options."""

from typing import Optional, Dict
from pathlib import Path
import logging
from io import BytesIO

from gtts import gTTS
from config.languages import LANG_CONFIG
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSEngine:
    """Generate speech from text in multiple languages."""
    
    def __init__(self, use_cloud: bool = False):
        self.use_cloud = use_cloud and Settings.USE_GOOGLE_CLOUD_TTS
        
        if self.use_cloud:
            try:
                from google.cloud import texttospeech
                self.cloud_client = texttospeech.TextToSpeechClient()
                logger.info("Using Google Cloud TTS")
            except Exception as e:
                logger.warning(f"Cloud TTS failed: {e}, using gTTS")
                self.use_cloud = False
                self.cloud_client = None
        else:
            self.cloud_client = None
    
    def synthesize(self, text: str, language: str, 
                   voice_id: Optional[str] = None) -> bytes:
        """
        Generate audio from text.
        
        Args:
            text: Text to speak
            language: Language code ('en', 'hi', 'te')
            voice_id: Specific voice selection
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not text:
            return b''
        
        if self.use_cloud:
            return self._synthesize_cloud(text, language, voice_id)
        else:
            return self._synthesize_gtts(text, language)
    
    def _synthesize_gtts(self, text: str, language: str) -> bytes:
        """Use gTTS (free, simpler voices)."""
        try:
            # Map to gTTS language codes
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'te': 'te',
                'ta': 'ta'
            }
            
            tts_lang = lang_map.get(language, 'en')
            
            # Split long text (gTTS has limits)
            max_chars = 500
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            
            return mp3_fp.read()
            
        except Exception as e:
            logger.error(f"gTTS failed: {e}")
            return b''
    
    def _synthesize_cloud(self, text: str, language: str, 
                          voice_id: Optional[str]) -> bytes:
        """Use Google Cloud TTS (higher quality, requires API key)."""
        from google.cloud import texttospeech
        
        # Map language codes
        lang_codes = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'te': 'te-IN',
            'ta': 'ta-IN'
        }
        
        lang_code = lang_codes.get(language, 'en-IN')
        
        # Select voice
        if voice_id and 'female' in voice_id:
            voice_name = f"{lang_code}-Standard-A"
        else:
            voice_name = f"{lang_code}-Standard-B"
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9  # Slightly slower for medical content
        )
        
        try:
            response = self.cloud_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            return response.audio_content
        except Exception as e:
            logger.error(f"Cloud TTS failed: {e}, falling back to gTTS")
            return self._synthesize_gtts(text, language)
    
    def get_available_voices(self, language: str) -> list:
        """Get list of available voices for language."""
        if language not in LANG_CONFIG:
            return []
        
        return LANG_CONFIG[language].get('voices', [])
    
    def save_audio(self, audio_bytes: bytes, output_path: Path):
        """Save audio bytes to file."""
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
        logger.info(f"Audio saved to {output_path}")