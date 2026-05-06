"""
SmartReader Pi Server - OCR Service
Handles text extraction from images using Tesseract and Google Vision API
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR extraction result"""
    text: str
    confidence: float
    detected_language: str
    paragraph_count: int


class OCRService:
    """
    Service for text extraction from images
    Supports Tesseract (offline) and Google Vision API (cloud)
    """
    
    def __init__(self):
        """Initialize OCR service"""
        self.tesseract_available = self._check_tesseract()
        self.google_vision_available = self._check_google_vision()
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR available")
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    def _check_google_vision(self) -> bool:
        """Check if Google Vision API is configured"""
        try:
            from google.cloud import vision
            # Check if credentials are set
            import os
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                logger.info("Google Vision API available")
                return True
            else:
                logger.warning("Google Vision API credentials not configured")
                return False
        except ImportError:
            logger.warning("Google Vision API library not installed")
            return False
    
    def extract_text(
        self,
        image: np.ndarray,
        engine: str = 'tesseract'
    ) -> OCRResult:
        """
        Extract text from image using specified OCR engine
        
        Args:
            image: Preprocessed image as numpy array
            engine: OCR engine to use ('tesseract' or 'cloud')
            
        Returns:
            OCRResult with extracted text and metadata
        """
        if engine == 'cloud' and self.google_vision_available:
            return self._extract_with_google_vision(image)
        elif self.tesseract_available:
            return self._extract_with_tesseract(image)
        else:
            logger.error("No OCR engine available")
            return OCRResult(
                text="",
                confidence=0.0,
                detected_language="unknown",
                paragraph_count=0
            )
    
    def _extract_with_tesseract(self, image: np.ndarray) -> OCRResult:
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Preprocessed image
            
        Returns:
            OCRResult
        """
        try:
            import pytesseract
            from PIL import Image
            
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)
            
            # Configure Tesseract for multiple languages
            # ara: Arabic, fra: French, eng: English
            config = '--oem 3 --psm 3'
            
            # Extract text
            text = pytesseract.image_to_string(
                pil_image,
                lang='ara+fra+eng',
                config=config
            )
            
            # Get detailed data for confidence and language detection
            data = pytesseract.image_to_data(
                pil_image,
                lang='ara+fra+eng',
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [
                int(conf) for conf in data['conf']
                if conf != '-1' and str(conf).isdigit()
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Detect language from text
            detected_language = self._detect_language(text)
            
            # Count paragraphs
            paragraph_count = self._count_paragraphs(text)
            
            logger.info(f"Tesseract OCR complete: {len(text)} chars, {paragraph_count} paragraphs")
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,
                detected_language=detected_language,
                paragraph_count=paragraph_count
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                detected_language="unknown",
                paragraph_count=0
            )
    
    def _extract_with_google_vision(self, image: np.ndarray) -> OCRResult:
        """
        Extract text using Google Vision API
        
        Args:
            image: Preprocessed image
            
        Returns:
            OCRResult
        """
        try:
            from google.cloud import vision
            import cv2
            
            # Initialize client
            client = vision.ImageAnnotatorClient()
            
            # Convert numpy array to bytes
            success, encoded_image = cv2.imencode('.png', image)
            if not success:
                raise Exception("Failed to encode image")
            
            content = encoded_image.tobytes()
            
            # Create Vision API image
            vision_image = vision.Image(content=content)
            
            # Perform text detection
            response = client.document_text_detection(image=vision_image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract full text
            text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Get confidence (average from pages)
            confidence = 0.0
            if response.full_text_annotation and response.full_text_annotation.pages:
                confidences = [
                    page.confidence
                    for page in response.full_text_annotation.pages
                    if hasattr(page, 'confidence')
                ]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Detect language
            detected_language = "unknown"
            if response.full_text_annotation and response.full_text_annotation.pages:
                for page in response.full_text_annotation.pages:
                    if page.property and page.property.detected_languages:
                        lang_code = page.property.detected_languages[0].language_code
                        detected_language = self._map_language_code(lang_code)
                        break
            
            # Count paragraphs
            paragraph_count = self._count_paragraphs(text)
            
            logger.info(f"Google Vision OCR complete: {len(text)} chars, {paragraph_count} paragraphs")
            
            return OCRResult(
                text=text.strip(),
                confidence=confidence,
                detected_language=detected_language,
                paragraph_count=paragraph_count
            )
            
        except Exception as e:
            logger.error(f"Google Vision OCR error: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                detected_language="unknown",
                paragraph_count=0
            )
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language from text content
        Simple heuristic based on character sets
        
        Args:
            text: Extracted text
            
        Returns:
            Language code ('arabic', 'french', 'english', or 'unknown')
        """
        if not text:
            return "unknown"
        
        # Count Arabic characters
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        
        # Count Latin characters
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = arabic_chars + latin_chars
        
        if total_chars == 0:
            return "unknown"
        
        # If more than 30% Arabic characters, classify as Arabic
        if arabic_chars / total_chars > 0.3:
            return "arabic"
        
        # For Latin scripts, use simple word matching
        # French has more accented characters and specific words
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'à', 'est']
        english_indicators = ['the', 'a', 'an', 'and', 'or', 'is', 'are', 'of', 'to', 'in']
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_indicators if f' {word} ' in text_lower)
        english_count = sum(1 for word in english_indicators if f' {word} ' in text_lower)
        
        if french_count > english_count:
            return "french"
        elif english_count > 0:
            return "english"
        
        return "unknown"
    
    def _map_language_code(self, lang_code: str) -> str:
        """
        Map ISO language code to app language
        
        Args:
            lang_code: ISO language code (e.g., 'ar', 'fr', 'en')
            
        Returns:
            App language code
        """
        mapping = {
            'ar': 'arabic',
            'fr': 'french',
            'en': 'english',
        }
        return mapping.get(lang_code, 'unknown')
    
    def _count_paragraphs(self, text: str) -> int:
        """
        Count paragraphs in text
        Paragraphs are separated by blank lines
        
        Args:
            text: Extracted text
            
        Returns:
            Number of paragraphs
        """
        if not text or not text.strip():
            return 0
        
        # Split by double newlines (blank lines)
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        # Filter out empty paragraphs
        non_empty = [p for p in paragraphs if p.strip()]
        
        return len(non_empty) if non_empty else 1
