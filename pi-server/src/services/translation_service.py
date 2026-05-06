"""
SmartReader Pi Server - Translation Service
Handles text translation between supported languages
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for text translation
    Supports Arabic, French, English, Darija
    """
    
    def __init__(self):
        """Initialize translation service"""
        self.translator_available = self._check_translator()
    
    def _check_translator(self) -> bool:
        """Check if translation library is available"""
        try:
            from googletrans import Translator
            logger.info("Google Translate available")
            return True
        except Exception as e:
            logger.warning(f"Google Translate not available: {e}")
            return False
    
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Optional[str]:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_language: Source language ('arabic', 'french', 'english', 'darija')
            target_language: Target language ('arabic', 'french', 'english', 'darija')
            
        Returns:
            Translated text, or None if translation fails
        """
        if not text or not text.strip():
            logger.error("Empty text provided for translation")
            return None
        
        if source_language == target_language:
            logger.info("Source and target languages are the same, returning original text")
            return text
        
        if not self.translator_available:
            logger.error("Translation service not available")
            return None
        
        try:
            from googletrans import Translator
            
            translator = Translator()
            
            # Map app languages to Google Translate language codes
            language_map = {
                'arabic': 'ar',
                'french': 'fr',
                'english': 'en',
                'darija': 'ar',  # Darija uses Arabic code
            }
            
            src_code = language_map.get(source_language, 'auto')
            dest_code = language_map.get(target_language, 'en')
            
            # Perform translation
            result = translator.translate(
                text,
                src=src_code,
                dest=dest_code
            )
            
            translated_text = result.text
            
            logger.info(f"Translation complete: {source_language} -> {target_language}")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code, or None if detection fails
        """
        if not text or not text.strip():
            return None
        
        if not self.translator_available:
            return None
        
        try:
            from googletrans import Translator
            
            translator = Translator()
            detection = translator.detect(text)
            
            # Map Google language codes to app languages
            reverse_map = {
                'ar': 'arabic',
                'fr': 'french',
                'en': 'english',
            }
            
            detected_lang = reverse_map.get(detection.lang, 'unknown')
            
            logger.info(f"Language detected: {detected_lang} (confidence: {detection.confidence})")
            return detected_lang
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return None
