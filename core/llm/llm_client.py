"""Unified LLM client supporting multiple backends."""

import os
import logging
from typing import Optional, Dict, Any
import json

from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """Unified interface for OpenAI, Gemini, and local models."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: 'openai', 'gemini', 'local', or None (auto-select)
        """
        self.provider = provider or self._auto_select_provider()
        self.client = None
        self._init_client()
    
    def _auto_select_provider(self) -> str:
        """Select best available provider."""
        if Settings.GEMINI_API_KEY:
            return 'gemini'
        elif Settings.OPENAI_API_KEY:
            return 'openai'
        else:
            return 'local'
    
    def _init_client(self):
        """Initialize specific client."""
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            self._init_local()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=Settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"OpenAI init failed: {e}")
            self._init_local()
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=Settings.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(Settings.GEMINI_MODEL)
            logger.info("Gemini client initialized")
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")
            self._init_local()
    
    def _init_local(self):
        """Initialize local HuggingFace model."""
        try:
            from transformers import pipeline
            self.client = pipeline(
                'text-generation',
                model='microsoft/DialoGPT-medium',  # Small, fast model
                max_new_tokens=500,
                do_sample=True,
                temperature=0.7
            )
            self.provider = 'local'
            logger.info("Local LLM initialized")
        except Exception as e:
            logger.error(f"Local model failed: {e}")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 500, 
                 temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific args
            
        Returns:
            Generated text
        """
        if self.client is None:
            return "Error: No LLM available"
        
        try:
            if self.provider == 'openai':
                return self._generate_openai(prompt, max_tokens, temperature)
            elif self.provider == 'gemini':
                return self._generate_gemini(prompt, max_tokens, temperature)
            else:
                return self._generate_local(prompt, max_tokens)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_openai(self, prompt: str, max_tokens: int, 
                         temperature: float) -> str:
        """OpenAI generation."""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _generate_gemini(self, prompt: str, max_tokens: int, 
                         temperature: float) -> str:
        """Gemini generation."""
        response = self.client.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': max_tokens,
                'temperature': temperature
            }
        )
        return response.text
    
    def _generate_local(self, prompt: str, max_tokens: int) -> str:
        """Local model generation."""
        # Format for conversational model
        formatted_prompt = f"User: {prompt}\nAssistant:"
        
        result = self.client(
            formatted_prompt,
            max_new_tokens=max_tokens,
            num_return_sequences=1
        )
        
        generated = result[0]['generated_text']
        # Extract only the assistant's response
        if 'Assistant:' in generated:
            generated = generated.split('Assistant:')[-1].strip()
        
        return generated
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client is not None