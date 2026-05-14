#!/usr/bin/env python3
"""
Test script for camera preview
Run this on the Pi to test the camera preview window
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.camera_preview import start_camera_preview, stop_camera_preview
import time

if __name__ == "__main__":
    print("Starting camera preview...")
    print("Press Ctrl+C to stop")
    
    try:
        start_camera_preview()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping camera preview...")
        stop_camera_preview()
        print("Done!")
