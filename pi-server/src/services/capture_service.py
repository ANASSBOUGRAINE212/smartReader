"""
SmartReader Pi Server - Capture Service
Handles camera control and image preprocessing
"""

import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CaptureService:
    """
    Service for camera capture and image preprocessing
    Handles Logitech C270 camera control and OpenCV preprocessing
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize capture service
        
        Args:
            camera_index: Camera device index (default: 0)
        """
        self.camera_index = camera_index
        self.camera: Optional[cv2.VideoCapture] = None
        
    def initialize_camera(self) -> bool:
        """
        Initialize camera connection
        
        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set camera resolution (C270 supports up to 1280x720)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            logger.info("Camera initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture image from camera
        
        Returns:
            Captured image as numpy array, or None if capture fails
        """
        try:
            if self.camera is None or not self.camera.isOpened():
                if not self.initialize_camera():
                    return None
            
            # TODO: Activate LED ring lighting via GPIO
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(LED_PIN, GPIO.OUT)
            # GPIO.output(LED_PIN, GPIO.HIGH)
            
            # Capture frame
            ret, frame = self.camera.read()
            
            # TODO: Deactivate LED ring lighting
            # GPIO.output(LED_PIN, GPIO.LOW)
            
            if not ret or frame is None:
                logger.error("Failed to capture frame")
                return None
            
            logger.info(f"Image captured: {frame.shape}")
            return frame
            
        except Exception as e:
            logger.error(f"Image capture error: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply OpenCV preprocessing to improve OCR accuracy
        - Convert to grayscale
        - Deskew (correct rotation)
        - Adjust contrast
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Deskew: detect and correct rotation
            gray = self._deskew(gray)
            
            # Adjust contrast using adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply slight Gaussian blur to reduce noise
            denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Apply adaptive thresholding for better text extraction
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            logger.info("Image preprocessing complete")
            return binary
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image
    
    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct image rotation (deskew)
        
        Args:
            image: Grayscale image
            
        Returns:
            Deskewed image
        """
        try:
            # Calculate skew angle using Hough transform
            coords = np.column_stack(np.where(image > 0))
            if len(coords) == 0:
                return image
            
            angle = cv2.minAreaRect(coords)[-1]
            
            # Adjust angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Only correct if angle is significant (> 0.5 degrees)
            if abs(angle) < 0.5:
                return image
            
            # Rotate image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            logger.info(f"Image deskewed by {angle:.2f} degrees")
            return rotated
            
        except Exception as e:
            logger.error(f"Deskew error: {e}")
            return image
    
    def release(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            logger.info("Camera released")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.release()
