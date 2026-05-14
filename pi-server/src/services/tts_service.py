"""
SmartReader Pi Server - TTS Service
Handles text-to-speech conversion using gTTS (Google Text-to-Speech)
"""

import os
import logging
from typing import Optional
import uuid

logger = logging.getLogger(__name__)


class TTSService:
    """
    Service for text-to-speech conversion
    Uses gTTS for fast and reliable speech synthesis
    """
    
    def __init__(self):
        """Initialize TTS service"""
        # Create audio directory if it doesn't exist
        self.audio_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'audio')
        os.makedirs(self.audio_dir, exist_ok=True)
        
        self.gtts_available = self._check_gtts()
        logger.info(f"TTS Service initialized. gTTS available: {self.gtts_available}")
    
    def _check_gtts(self) -> bool:
        """Check if gTTS is available"""
        try:
            from gtts import gTTS
            logger.info("gTTS available")
            return True
        except ImportError:
            logger.warning("gTTS not installed. Install with: pip install gtts")
            return False
    
    def synthesize(
        self,
        text: str,
        language: str = 'french',
        rate: float = 1.0,
        pitch: str = 'normal',
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech audio from text using gTTS
        
        Args:
            text: Text to convert to speech
            language: Target language ('french' or 'english')
            rate: Speech rate (not used by gTTS, kept for compatibility)
            pitch: Speech pitch (not used by gTTS, kept for compatibility)
            output_path: Optional output path (auto-generated if None)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return None
        
        if not self.gtts_available:
            logger.error("gTTS not available")
            return None
        
        try:
            from gtts import gTTS
            
            # Map language codes
            lang_map = {
                'french': 'fr',
                'english': 'en',
            }
            tts_lang = lang_map.get(language, 'fr')
            
            # Generate output path if not provided
            if output_path is None:
                audio_filename = f"{uuid.uuid4()}.mp3"
                output_path = os.path.join(self.audio_dir, audio_filename)
            
            # Generate speech
            logger.info(f"Generating TTS for {len(text)} characters in {language}")
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(output_path)
            
            logger.info(f"TTS audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    def play_audio(self, audio_path: str) -> bool:
        """
        Play audio file on Pi speaker
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if playback succeeded, False otherwise
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        try:
            # Try mpg123 first (faster)
            result = os.system(f"mpg123 -q {audio_path}")
            if result == 0:
                logger.info(f"Audio played successfully: {audio_path}")
                return True
            
            # Fallback to omxplayer
            result = os.system(f"omxplayer {audio_path}")
            if result == 0:
                logger.info(f"Audio played successfully with omxplayer: {audio_path}")
                return True
            
            logger.error("Failed to play audio with both mpg123 and omxplayer")
            return False
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False
    
    def cleanup_old_audio(self, max_files: int = 50):
        """
        Clean up old audio files to save disk space
        
        Args:
            max_files: Maximum number of audio files to keep
        """
        try:
            audio_files = [
                os.path.join(self.audio_dir, f)
                for f in os.listdir(self.audio_dir)
                if f.endswith('.mp3')
            ]
            
            # Sort by modification time
            audio_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Delete oldest files if we exceed max_files
            if len(audio_files) > max_files:
                files_to_delete = audio_files[:-max_files]
                for file_path in files_to_delete:
                    os.remove(file_path)
                    logger.info(f"Deleted old audio file: {file_path}")
                
                logger.info(f"Cleaned up {len(files_to_delete)} old audio files")
        
        except Exception as e:
            logger.error(f"Audio cleanup error: {e}")
    
    def get_audio_path(self, filename: str) -> str:
        """
        Get full path to audio file
        
        Args:
            filename: Audio filename
            
        Returns:
            Full path to audio file
        """
        return os.path.join(self.audio_dir, filename)
