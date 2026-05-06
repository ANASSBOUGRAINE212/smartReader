"""
Mock Capture Service for testing without camera hardware
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

class MockCaptureService:
    """Mock camera service that generates test images"""
    
    def __init__(self):
        self.led_enabled = False
    
    def capture_image(self):
        """Generate a mock image with sample text"""
        # Create a white image with black text
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add sample text
        sample_text = """SmartReader Test Document
        
This is a sample document for testing.
The camera is not connected, so this
is a mock image with readable text.

You can test OCR and TTS features
with this generated content.

مرحبا بك في SmartReader
Bonjour et bienvenue"""
        
        try:
            # Try to use a default font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), sample_text, fill='black', font=font)
        
        # Convert PIL image to numpy array (OpenCV format)
        return np.array(img)
    
    def preprocess_image(self, image):
        """Return image as-is for mock"""
        return image
    
    def enable_led_ring(self):
        """Mock LED control"""
        self.led_enabled = True
        print("Mock: LED ring enabled")
    
    def disable_led_ring(self):
        """Mock LED control"""
        self.led_enabled = False
        print("Mock: LED ring disabled")
