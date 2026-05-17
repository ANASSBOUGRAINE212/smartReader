# Run from SSH on laptop:
# DISPLAY=:0 python blind_assistant_server.py

import os
os.environ["DISPLAY"] = ":0"

import asyncio
import base64
import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ultralytics import YOLO
import uvicorn

# Try to import picamera2 for Pi camera support
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Warning: picamera2 not available. Pi camera mode disabled.")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blind_detections.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Blind Assistant Server")

# Load YOLO model
logger.info("Loading YOLOv8 nano model...")
model = YOLO("yolov8n.pt")
logger.info("Model loaded successfully")

# Relevant classes for blind assistance
RELEVANT_CLASSES = {
    'person', 'chair', 'car', 'bicycle', 'bottle', 
    'dining table', 'bed', 'dog', 'cat', 'stairs',
    'couch', 'door', 'cup', 'knife', 'spoon', 'bowl'
}

# OpenCV window setup
WINDOW_NAME = "Blind Assistant - Live View"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 800, 600)

# Pi Camera instance (if available)
picam: Optional[Picamera2] = None

def init_pi_camera():
    """Initialize Pi camera"""
    global picam
    if not PICAMERA_AVAILABLE:
        return False
    
    try:
        picam = Picamera2()
        config = picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam.configure(config)
        picam.start()
        logger.info("Pi camera initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Pi camera: {e}")
        return False

def capture_pi_camera():
    """Capture frame from Pi camera"""
    if picam is None:
        return None
    
    try:
        frame = picam.capture_array()
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame_bgr
    except Exception as e:
        logger.error(f"Error capturing from Pi camera: {e}")
        return None

def calculate_distance(bbox_height, img_height):
    """
    Calculate relative distance based on bounding box height ratio
    """
    ratio = bbox_height / img_height
    
    if ratio > 0.5:
        return "very close"
    elif ratio > 0.3:
        return "close"
    elif ratio > 0.15:
        return "nearby"
    else:
        return "far"

def process_frame(img_bgr, source="phone"):
    """
    Process frame with YOLO detection
    """
    try:
        img_height = img_bgr.shape[0]
        
        # Run YOLO detection
        results = model(img_bgr, imgsz=320, conf=0.45, verbose=False)
        
        # Process detections
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            
            for box in boxes:
                # Get class name
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                # Only include relevant classes
                if class_name not in RELEVANT_CLASSES:
                    continue
                
                # Get confidence
                confidence = float(box.conf[0])
                
                # Get bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox_height = y2 - y1
                
                # Calculate distance
                distance = calculate_distance(bbox_height, img_height)
                
                detections.append({
                    "label": class_name,
                    "confidence": round(confidence, 2),
                    "distance": distance
                })
        
        # Draw results on image
        annotated_frame = results[0].plot()
        
        # Add source label
        cv2.putText(annotated_frame, f"Source: {source.upper()}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Update window title with object count
        cv2.setWindowTitle(WINDOW_NAME, f"{WINDOW_NAME} - {len(detections)} objects detected ({source})")
        
        # Display in OpenCV window
        cv2.imshow(WINDOW_NAME, annotated_frame)
        cv2.waitKey(1)
        
        # Log detections
        if detections:
            logger.info(f"[{source}] Detected {len(detections)} objects: {[d['label'] for d in detections]}")
        
        return detections
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for receiving frames and sending detections
    Supports both phone camera and Pi camera modes
    """
    await websocket.accept()
    logger.info("Client connected")
    
    camera_mode = "phone"  # Default to phone camera
    audio_output = "phone"  # Default to phone speaker
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle mode change
            if "mode" in message:
                camera_mode = message["mode"]
                logger.info(f"Camera mode changed to: {camera_mode}")
                
                if camera_mode == "pi" and not picam:
                    # Try to initialize Pi camera
                    if not init_pi_camera():
                        await websocket.send_text(json.dumps({
                            "error": "Pi camera not available",
                            "detections": []
                        }))
                        camera_mode = "phone"
                continue
            
            # Handle audio output change
            if "audio_output" in message:
                audio_output = message["audio_output"]
                logger.info(f"Audio output changed to: {audio_output}")
                continue
            
            # Process frame based on mode
            if camera_mode == "pi":
                # Capture from Pi camera
                img_bgr = capture_pi_camera()
                if img_bgr is None:
                    await websocket.send_text(json.dumps({
                        "error": "Failed to capture from Pi camera",
                        "detections": []
                    }))
                    continue
                
                detections = process_frame(img_bgr, source="pi")
            
            elif "image" in message:
                # Process phone camera frame
                image_base64 = message["image"]
                
                # Decode base64 to image
                image_data = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_data))
                
                # Convert to OpenCV format (BGR)
                img_array = np.array(image)
                if len(img_array.shape) == 2:  # Grayscale
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
                elif img_array.shape[2] == 4:  # RGBA
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                detections = process_frame(img_bgr, source="phone")
            else:
                continue
            
            # Send detections back
            response = {
                "detections": detections,
                "timestamp": datetime.now().isoformat(),
                "camera_mode": camera_mode,
                "audio_output": audio_output
            }
            await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "running",
        "service": "Blind Assistant Server",
        "model": "YOLOv8 nano",
        "pi_camera_available": PICAMERA_AVAILABLE,
        "camera_initialized": picam is not None
    }

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    if picam:
        try:
            picam.stop()
            picam.close()
        except:
            pass
    cv2.destroyAllWindows()
    logger.info("Server shutdown")

if __name__ == "__main__":
    logger.info("Starting Blind Assistant Server on port 8000...")
    logger.info(f"Pi Camera Available: {PICAMERA_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
