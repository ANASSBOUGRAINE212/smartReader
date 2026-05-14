"""
Camera Preview Service
Shows live camera feed in a native window on the Pi
"""

import cv2
import threading
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class CameraPreview:
    """Manages camera preview window"""
    
    def __init__(self):
        self.camera: Optional[cv2.VideoCapture] = None
        self.preview_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.window_name = "SmartReader Camera"
        
    def start_preview(self):
        """Start camera preview in a new window"""
        if self.is_running:
            logger.info("Preview already running")
            return
            
        self.is_running = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
        logger.info("Camera preview started")
        
    def stop_preview(self):
        """Stop camera preview and close window"""
        self.is_running = False
        
        # Don't try to join if we're being called from within the preview thread
        if self.preview_thread and threading.current_thread() != self.preview_thread:
            self.preview_thread.join(timeout=2)
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        cv2.destroyAllWindows()
        logger.info("Camera preview stopped")
        
    def _preview_loop(self):
        """Main preview loop running in separate thread"""
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                self.is_running = False
                return
                
            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Create window
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 800, 600)
            
            logger.info("Camera preview window opened")
            
            while self.is_running:
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                    
                # Add overlay text
                self._add_overlay(frame)
                
                # Display frame
                cv2.imshow(self.window_name, frame)
                
                # Check for window close or ESC key
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    logger.info("Preview window closed by user")
                    break
                    
        except Exception as e:
            logger.exception(f"Error in preview loop: {e}")
        finally:
            self.stop_preview()
            
    def _add_overlay(self, frame):
        """Add informational overlay to frame"""
        height, width = frame.shape[:2]
        
        # Add semi-transparent overlay at top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 60), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Add text
        cv2.putText(
            frame,
            "SmartReader Camera Preview",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.putText(
            frame,
            "Press ESC to close | Ready to scan",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )
        
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from the camera"""
        if not self.camera or not self.camera.isOpened():
            logger.error("Camera not available for capture")
            return None
            
        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None
            
        return frame
    
    def capture_with_preview(self, preview_duration: int = 10) -> Optional[np.ndarray]:
        """
        Show preview for specified duration, then capture frame
        
        Args:
            preview_duration: Duration in seconds to show preview before capture
            
        Returns:
            Captured frame or None if failed
        """
        import time
        
        logger.info(f"Starting {preview_duration}s preview before capture")
        
        # Start preview if not already running
        was_running = self.is_running
        if not was_running:
            self.start_preview()
            time.sleep(0.5)  # Give camera time to initialize
        
        # Wait for preview duration with countdown
        for remaining in range(preview_duration, 0, -1):
            if not self.is_running:
                logger.error("Preview stopped during countdown")
                return None
            time.sleep(1)
            logger.info(f"Capturing in {remaining} seconds...")
        
        # Capture frame
        frame = self.capture_frame()
        
        # Stop preview if we started it (set flag but don't join thread)
        if not was_running:
            self.is_running = False
            if self.camera:
                self.camera.release()
                self.camera = None
            cv2.destroyAllWindows()
            logger.info("Preview closed after capture")
        
        logger.info("Frame captured successfully")
        return frame


# Global instance
_preview_instance: Optional[CameraPreview] = None


def get_preview_instance() -> CameraPreview:
    """Get or create the global preview instance"""
    global _preview_instance
    if _preview_instance is None:
        _preview_instance = CameraPreview()
    return _preview_instance


def start_camera_preview():
    """Start the camera preview window"""
    preview = get_preview_instance()
    preview.start_preview()


def stop_camera_preview():
    """Stop the camera preview window"""
    preview = get_preview_instance()
    preview.stop_preview()


def is_preview_running() -> bool:
    """Check if preview is currently running"""
    preview = get_preview_instance()
    return preview.is_running
