"""
SmartReader Pi Server - Settings Service
Manages configuration persistence and validation
"""

import os
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SettingsService:
    """
    Service for managing application settings
    Handles persistence, validation, and default values
    """
    
    DEFAULT_SETTINGS = {
        'language': 'french',
        'speechRate': 1.0,
        'speechPitch': 'normal',
        'readingMode': 'continuous',
        'audioOutput': 'pi-speaker',
        'ocrEngine': 'tesseract'
    }
    
    VALID_LANGUAGES = ['arabic', 'french', 'english', 'darija']
    VALID_PITCHES = ['low', 'normal', 'high']
    VALID_READING_MODES = ['continuous', 'paragraph', 'section']
    VALID_AUDIO_OUTPUTS = ['pi-speaker', 'phone', 'bluetooth']
    VALID_OCR_ENGINES = ['tesseract', 'cloud']
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize settings service
        
        Args:
            data_dir: Directory for storing settings
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '../../data')
        
        self.data_dir = data_dir
        self.settings_file = os.path.join(data_dir, 'settings.json')
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize settings file with defaults if it doesn't exist
        if not os.path.exists(self.settings_file):
            self.save_settings(self.DEFAULT_SETTINGS)
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file
        
        Returns:
            Settings dictionary
        """
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            merged_settings = {**self.DEFAULT_SETTINGS, **settings}
            
            logger.info("Settings loaded successfully")
            return merged_settings
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save settings to file with validation
        
        Args:
            settings: Settings dictionary (can be partial)
            
        Returns:
            Updated settings dictionary
        """
        try:
            # Load current settings
            current_settings = self.load_settings()
            
            # Update with new values
            current_settings.update(settings)
            
            # Validate settings
            validated_settings = self._validate_settings(current_settings)
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(validated_settings, f, ensure_ascii=False, indent=2)
            
            logger.info("Settings saved successfully")
            return validated_settings
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate settings values
        
        Args:
            settings: Settings dictionary
            
        Returns:
            Validated settings dictionary
        """
        validated = settings.copy()
        
        # Validate language
        if validated.get('language') not in self.VALID_LANGUAGES:
            logger.warning(f"Invalid language: {validated.get('language')}, using default")
            validated['language'] = self.DEFAULT_SETTINGS['language']
        
        # Validate speech rate (0.5 - 2.0)
        try:
            rate = float(validated.get('speechRate', 1.0))
            if rate < 0.5 or rate > 2.0:
                logger.warning(f"Invalid speech rate: {rate}, using default")
                validated['speechRate'] = self.DEFAULT_SETTINGS['speechRate']
            else:
                validated['speechRate'] = rate
        except (ValueError, TypeError):
            logger.warning(f"Invalid speech rate type, using default")
            validated['speechRate'] = self.DEFAULT_SETTINGS['speechRate']
        
        # Validate speech pitch
        if validated.get('speechPitch') not in self.VALID_PITCHES:
            logger.warning(f"Invalid speech pitch: {validated.get('speechPitch')}, using default")
            validated['speechPitch'] = self.DEFAULT_SETTINGS['speechPitch']
        
        # Validate reading mode
        if validated.get('readingMode') not in self.VALID_READING_MODES:
            logger.warning(f"Invalid reading mode: {validated.get('readingMode')}, using default")
            validated['readingMode'] = self.DEFAULT_SETTINGS['readingMode']
        
        # Validate audio output
        if validated.get('audioOutput') not in self.VALID_AUDIO_OUTPUTS:
            logger.warning(f"Invalid audio output: {validated.get('audioOutput')}, using default")
            validated['audioOutput'] = self.DEFAULT_SETTINGS['audioOutput']
        
        # Validate OCR engine
        if validated.get('ocrEngine') not in self.VALID_OCR_ENGINES:
            logger.warning(f"Invalid OCR engine: {validated.get('ocrEngine')}, using default")
            validated['ocrEngine'] = self.DEFAULT_SETTINGS['ocrEngine']
        
        return validated
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Reset settings to default values
        
        Returns:
            Default settings dictionary
        """
        return self.save_settings(self.DEFAULT_SETTINGS.copy())
