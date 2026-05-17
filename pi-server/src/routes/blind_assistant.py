"""
Blind Assistant WebSocket Route
Real-time object detection for navigation assistance
"""

import os
os.environ["DISPLAY"] = ":0"

import base64
import json
import logging
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from flask_socketio import emit, disconnect
from ultralytics import YOLO

# Try to import OCR for text reading
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: pytesseract not available. Text reading disabled.")



logger = logging.getLogger(__name__)

# Load YOLO model (singleton)
_yolo_model = None

# OpenCV window setup
WINDOW_NAME = "Blind Assistant - Live View"
_window_initialized = False

# Priority levels for objects
PRIORITY_HIGH = {
    'person', 'car', 'bicycle', 'motorcycle', 'bus', 'truck', 
    'dog', 'cat', 'stairs', 'stop sign'
}

PRIORITY_MEDIUM = {
    'chair', 'couch', 'bench', 'door', 'fire hydrant', 
    'parking meter', 'backpack', 'handbag', 'umbrella'
}

PRIORITY_LOW = {
    'bed', 'dining table', 'toilet', 'bottle', 'cup', 'bowl',
    'cell phone', 'laptop', 'keyboard', 'mouse', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'bird'
}

# All relevant classes
RELEVANT_CLASSES = PRIORITY_HIGH | PRIORITY_MEDIUM | PRIORITY_LOW

# Hazards that need immediate attention
HAZARDS = {'car', 'bicycle', 'motorcycle', 'bus', 'truck', 'stairs'}

# Text-readable objects - trigger OCR
TEXT_OBJECTS = {'book', 'laptop', 'cell phone', 'stop sign'}

# Object tracking for smart alerts
_object_history = {}  # Track objects across frames
_last_alert_time = {}  # Prevent alert spam
_alert_cooldown = 3.0  # Seconds between same alerts


def get_yolo_model():
    """Get or initialize YOLO model"""
    global _yolo_model
    if _yolo_model is None:
        logger.info("Loading YOLOv8 nano model...")
        _yolo_model = YOLO("yolov8n.pt")
        logger.info("YOLO model loaded successfully")
    return _yolo_model


def init_opencv_window():
    """Initialize OpenCV window"""
    global _window_initialized
    if not _window_initialized:
        try:
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 800, 600)
            _window_initialized = True
        except Exception as e:
            logger.warning(f"Could not create OpenCV window (running headless?): {e}")
            _window_initialized = False





def calculate_distance(bbox_height, img_height):
    """Calculate relative distance based on bounding box height ratio"""
    ratio = bbox_height / img_height
    
    if ratio > 0.6:
        return "very close", 1
    elif ratio > 0.35:
        return "close", 2
    elif ratio > 0.18:
        return "nearby", 3
    elif ratio > 0.08:
        return "far", 4
    else:
        return "very far", 5


def calculate_direction(bbox_center_x, img_width):
    """Calculate direction based on bounding box center position"""
    # Divide image into 5 zones
    if bbox_center_x < img_width * 0.25:
        return "far left", 1
    elif bbox_center_x < img_width * 0.4:
        return "left", 2
    elif bbox_center_x < img_width * 0.6:
        return "ahead", 3  # Changed from "center" to "ahead"
    elif bbox_center_x < img_width * 0.75:
        return "right", 4
    else:
        return "far right", 5


def get_priority(label):
    """Get priority level for an object"""
    if label in PRIORITY_HIGH:
        return 1
    elif label in PRIORITY_MEDIUM:
        return 2
    else:
        return 3


def should_alert(label, distance_name, direction_name):
    """Determine if we should alert about this object"""
    import time
    
    # Create unique key for this detection
    key = f"{label}_{distance_name}_{direction_name}"
    current_time = time.time()
    
    # Check cooldown
    if key in _last_alert_time:
        if current_time - _last_alert_time[key] < _alert_cooldown:
            return False
    
    # Update alert time
    _last_alert_time[key] = current_time
    return True


def generate_smart_message(detections):
    """Generate intelligent, context-aware alert message"""
    if not detections:
        return None
    
    # Separate by priority and distance
    critical = []  # Very close hazards
    important = []  # Close high-priority objects
    notable = []  # Other relevant objects
    
    for d in detections:
        label = d['label']
        distance = d['distance']
        distance_level = d['distance_level']
        direction = d['direction']
        
        # Critical: Very close hazards or people
        if distance == 'very close' and (label in HAZARDS or label == 'person'):
            critical.append(d)
        # Important: Close high-priority objects
        elif distance in ['very close', 'close'] and get_priority(label) == 1:
            important.append(d)
        # Notable: Medium priority objects that are close
        elif distance in ['very close', 'close', 'nearby'] and get_priority(label) == 2:
            notable.append(d)
    
    # Build message with priority
    messages = []
    
    # Critical alerts (immediate danger)
    if critical:
        for obj in critical[:2]:  # Max 2 critical alerts
            if obj['label'] in HAZARDS:
                messages.append(f"Warning! {obj['label']} {obj['distance']} {obj['direction']}")
            else:
                messages.append(f"Person {obj['distance']} {obj['direction']}")
    
    # Important alerts
    elif important:
        # Group people
        people = [o for o in important if o['label'] == 'person']
        others = [o for o in important if o['label'] != 'person']
        
        if people:
            if len(people) == 1:
                messages.append(f"Person {people[0]['distance']}, {people[0]['direction']}")
            else:
                # Multiple people
                directions = [p['direction'] for p in people[:3]]
                messages.append(f"{len(people)} people nearby")
        
        # Add one other important object
        if others and len(messages) < 2:
            obj = others[0]
            messages.append(f"{obj['label']} {obj['distance']}, {obj['direction']}")
    
    # Notable alerts (only if nothing more important)
    elif notable:
        obj = notable[0]
        messages.append(f"{obj['label']} {obj['distance']}, {obj['direction']}")
    
    return ". ".join(messages) if messages else None


def process_frame(img_bgr, source="phone"):
    """Process frame with YOLO detection"""
    try:
        if img_bgr is None:
            logger.error("Received None image for processing")
            return [], None
        
        model = get_yolo_model()
        init_opencv_window()
        
        img_height = img_bgr.shape[0]
        img_width = img_bgr.shape[1]
        
        # Run YOLO detection with lower confidence for more detections
        results = model(img_bgr, imgsz=320, conf=0.30, verbose=False)
        
        # Process detections
        detections = []
        text_detected = False
        text_content = None
        
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            
            for box in boxes:
                try:
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
                    bbox_center_x = (x1 + x2) / 2
                    
                    # Calculate distance and direction
                    distance_name, distance_level = calculate_distance(bbox_height, img_height)
                    direction_name, direction_level = calculate_direction(bbox_center_x, img_width)
                    
                    detections.append({
                        "label": class_name,
                        "confidence": round(confidence, 2),
                        "distance": distance_name,
                        "distance_level": distance_level,
                        "direction": direction_name,
                        "direction_level": direction_level,
                        "priority": get_priority(class_name)
                    })
                    
                    # Check if text-readable object is close
                    if class_name in TEXT_OBJECTS and distance_name in ['very close', 'close'] and OCR_AVAILABLE:
                        text_detected = True
                        # Extract region for OCR
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        roi = img_bgr[y1:y2, x1:x2]
                        
                        # Perform OCR on region
                        try:
                            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                            text = pytesseract.image_to_string(roi_rgb, lang='eng+fra')
                            text = text.strip()
                            if text and len(text) > 3:  # Only if meaningful text found
                                text_content = text
                                logger.info(f"Text detected in {class_name}: {text[:50]}...")
                        except Exception as e:
                            logger.error(f"OCR error: {e}")
                except Exception as e:
                    logger.error(f"Error processing detection box: {e}")
                    continue
        
        # Draw results on image
        try:
            annotated_frame = results[0].plot()
            
            # Add source label and detection count
            cv2.putText(annotated_frame, f"Source: {source.upper()} | Objects: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Try to display in OpenCV window (skip if headless)
            if _window_initialized:
                try:
                    cv2.setWindowTitle(WINDOW_NAME, f"{WINDOW_NAME} - {len(detections)} objects ({source})")
                    cv2.imshow(WINDOW_NAME, annotated_frame)
                    cv2.waitKey(1)
                except Exception as e:
                    logger.debug(f"Could not update window: {e}")
        except Exception as e:
            logger.error(f"Error drawing results: {e}")
        
        # Log detections
        if detections:
            logger.info(f"[{source}] Detected {len(detections)} objects: {[(d['label'], d['direction'], d['distance']) for d in detections]}")
        
        return detections, text_content
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}", exc_info=True)
        return [], None


def register_blind_assistant_events(socketio):
    """Register blind assistant WebSocket events"""
    
    @socketio.on('connect', namespace='/ws/blind-assistant')
    def handle_connect():
        """Handle client connection"""
        logger.info("Blind assistant client connected")
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect', namespace='/ws/blind-assistant')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info("Blind assistant client disconnected")
        
        # Close OpenCV window
        try:
            cv2.destroyAllWindows()
        except:
            pass
    
    @socketio.on('stop', namespace='/ws/blind-assistant')
    def handle_stop():
        """Handle stop request from client"""
        logger.info("Blind assistant stopped by client")
        
        # Close OpenCV window
        try:
            cv2.destroyAllWindows()
        except:
            pass
        emit('stopped', {'status': 'stopped'})
    

    
    @socketio.on('audio_output', namespace='/ws/blind-assistant')
    def handle_audio_output(data):
        """Handle audio output change"""
        audio_output = data.get('output', 'phone')
        logger.info(f"Audio output changed to: {audio_output}")
        emit('audio_output_changed', {'output': audio_output})
    
    @socketio.on('frame', namespace='/ws/blind-assistant')
    def handle_frame(data):
        """Handle incoming frame for detection (phone camera only)"""
        try:
            # Process phone camera frame
            image_base64 = data.get('image')
            if not image_base64:
                return
            
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
            
            # Process frame
            detections, text_content = process_frame(img_bgr, source='phone')
            
            # Send detections back
            response = {
                'detections': detections,
                'camera_mode': 'phone'
            }
            
            # Add text if found
            if text_content:
                response['text'] = text_content
            
            emit('detections', response)
            
        except Exception as e:
            logger.error(f"Error handling frame: {e}")
            emit('error', {'message': str(e)})
    
    logger.info("Blind assistant WebSocket events registered")
