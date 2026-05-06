"""
SmartReader Pi Server - TTS Service
Handles text-to-speech synthesis using Coqui TTS and Google TTS
"""

from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


class TTSService:
    """
    Service for text-to-speech synthesis
    Supports Coqui TTS (primary) and Google TTS (fallback)
    Languages: Arabic, French, English, Darija
    """
    
    def __init__(self):
        """Initialize TTS service"""
        self.coqui_available = self._check_coqui()
        self.google_tts_available = self._check_google_tts()
        self.audio_dir = os.path.join(os.path.dirname(__file__), '../../audio')
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def _check_coqui(self) -> bool:
        """Check if Coqui TTS is available"""
        try:
            from TTS.api import TTS
            logger.info("Coqui TTS available")
            return True
        except Exception as e:
            logger.warning(f"Coqui TTS not available: {e}")
            return False
    
    def _check_google_tts(self) -> bool:
        """Check if Google TTS is configured"""
        try:
            from google.cloud import texttospeech
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.info("Google TTS available")
                return True
            else:
                logger.warning("Google TTS credentials not configured")
                return False
        except ImportError:
            logger.warning("Google TTS library not installed")
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
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            language: Target language ('arabic', 'french', 'english', 'darija')
            rate: Speech rate (0.5 - 2.0)
            pitch: Speech pitch ('low', 'normal', 'high')
            output_path: Optional output file path
            
        Returns:
            Path to generated audio file, or None if synthesis fails
        """
        if not text or not text.strip():
            logger.error("Empty text provided for TTS")
            return None
        
        # Validate rate
        rate = max(0.5, min(2.0, rate))
        
        # Try Coqui TTS first, fallback to Google TTS
        if self.coqui_available:
            return self._synthesize_with_coqui(text, language, rate, pitch, output_path)
        elif self.google_tts_available:
            return self._synthesize_with_google(text, language, rate, pitch, output_path)
        else:
            logger.error("No TTS engine available")
            return None
    
    def _synthesize_with_coqui(
        self,
        text: str,
        language: str,
        rate: float,
        pitch: str,
        output_path: Optional[str]
    ) -> Optional[str]:
        """
        Synthesize speech using Coqui TTS
        
        Args:
            text: Text to synthesize
            language: Target language
            rate: Speech rate
            pitch: Speech pitch
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            from TTS.api import TTS
            
            # Map language to Coqui model
            model_map = {
                'arabic': 'tts_models/ar/cv/vits',
                'french': 'tts_models/fr/css10/vits',
                'english': 'tts_models/en/ljspeech/tacotron2-DDC',
                'darija': 'tts_models/ar/cv/vits',  # Use Arabic model for Darija
            }
            
            model_name = model_map.get(language, model_map['french'])
            
            # Initialize TTS model
            tts = TTS(model_name=model_name)
            
            # Generate output path if not provided
            if output_path is None:
                import uuid
                filename = f"{uuid.uuid4()}.wav"
                output_path = os.path.join(self.audio_dir, filename)
            
            # Synthesize speech
            # Note: Coqui TTS doesn't directly support rate/pitch adjustment
            # These would need to be applied post-processing with audio libraries
            tts.tts_to_file(text=text, file_path=output_path)
            
            # Apply rate and pitch adjustments if needed
            if rate != 1.0 or pitch != 'normal':
                output_path = self._adjust_audio(output_path, rate, pitch)
            
            logger.info(f"Coqui TTS synthesis complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis error: {e}")
            return None
    
    def _synthesize_with_google(
        self,
        text: str,
        language: str,
        rate: float,
        pitch: str,
        output_path: Optional[str]
    ) -> Optional[str]:
        """
        Synthesize speech using Google TTS
        
        Args:
            text: Text to synthesize
            language: Target language
            rate: Speech rate
            pitch: Speech pitch
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            from google.cloud import texttospeech
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Map language to Google TTS language code
            language_map = {
                'arabic': 'ar-XA',
                'french': 'fr-FR',
                'english': 'en-US',
                'darija': 'ar-XA',  # Use Arabic for Darija
            }
            
            lang_code = language_map.get(language, 'fr-FR')
            
            # Set synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Map pitch to semitones
            pitch_map = {
                'low': -2.0,
                'normal': 0.0,
                'high': 2.0
            }
            pitch_value = pitch_map.get(pitch, 0.0)
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=rate,
                pitch=pitch_value
            )
            
            # Perform synthesis
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Generate output path if not provided
            if output_path is None:
                import uuid
                filename = f"{uuid.uuid4()}.mp3"
                output_path = os.path.join(self.audio_dir, filename)
            
            # Write audio to file
            with open(output_path, 'wb') as out:
                out.write(response.audio_content)
            
            logger.info(f"Google TTS synthesis complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Google TTS synthesis error: {e}")
            return None
    
    def _adjust_audio(
        self,
        audio_path: str,
        rate: float,
        pitch: str
    ) -> str:
        """
        Adjust audio rate and pitch using pydub
        
        Args:
            audio_path: Path to audio file
            rate: Speech rate multiplier
            pitch: Pitch adjustment
            
        Returns:
            Path to adjusted audio file
        """
        try:
            from pydub import AudioSegment
            from pydub.effects import speedup
            
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Adjust speed (rate)
            if rate != 1.0:
                # Speed up or slow down
                if rate > 1.0:
                    audio = speedup(audio, playback_speed=rate)
                else:
                    # Slow down by changing frame rate
                    audio = audio._spawn(
                        audio.raw_data,
                        overrides={'frame_rate': int(audio.frame_rate * rate)}
                    )
                    audio = audio.set_frame_rate(44100)
            
            # Adjust pitch (requires octaves parameter)
            pitch_map = {
                'low': -2,
                'normal': 0,
                'high': 2
            }
            octaves = pitch_map.get(pitch, 0) / 12.0
            
            if octaves != 0:
                new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
                audio = audio._spawn(
                    audio.raw_data,
                    overrides={'frame_rate': new_sample_rate}
                )
                audio = audio.set_frame_rate(44100)
            
            # Save adjusted audio
            adjusted_path = audio_path.replace('.wav', '_adjusted.wav').replace('.mp3', '_adjusted.mp3')
            audio.export(adjusted_path, format='mp3' if audio_path.endswith('.mp3') else 'wav')
            
            # Remove original file
            os.remove(audio_path)
            
            logger.info(f"Audio adjusted: rate={rate}, pitch={pitch}")
            return adjusted_path
            
        except Exception as e:
            logger.error(f"Audio adjustment error: {e}")
            return audio_path
    
    def get_audio_path(self, filename: str) -> str:
        """
        Get full path to audio file
        
        Args:
            filename: Audio filename
            
        Returns:
            Full path to audio file
        """
        return os.path.join(self.audio_dir, filename)
