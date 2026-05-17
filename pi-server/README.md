# SmartReader Pi Server

Flask-based REST API server running on Raspberry Pi 3B for document scanning, OCR, text-to-speech, and blind assistance with real-time object detection.

## Features

- **REST API**: Flask-based endpoints for mobile app communication
- **WebSocket Streaming**: Real-time audio and video streaming
- **Camera Control**: Logitech C270 camera with LED ring lighting
- **OCR Processing**: Tesseract (offline) and Google Vision API (cloud)
- **Multi-language TTS**: Arabic, French, English, and Darija support
- **Translation Service**: Text translation between languages
- **Blind Assistant**: YOLOv8-based real-time object detection for navigation
- **Reading History**: Persistent storage of scanned documents
- **Settings Management**: Customizable language, speech, and audio preferences
- **Dual Camera Support**: Phone camera and Raspberry Pi camera modes

## Prerequisites

- Python 3.9+
- Raspberry Pi 3B or 4
- Logitech C270 camera with LED ring lighting
- Tesseract OCR installed
- GPIO-connected speaker (optional)
- YOLOv8 model for object detection
- picamera2 library (for Pi camera support)

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (Raspberry Pi OS)
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara tesseract-ocr-fra tesseract-ocr-eng
```

## Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python src/app.py
```

The server will start on `http://0.0.0.0:5000` and be accessible at `http://smartreader.local:5000` via mDNS.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m property      # Property-based tests only
```

## Project Structure

```
pi-server/
├── src/
│   ├── services/       # Business logic services
│   ├── routes/         # API route handlers
│   ├── utils/          # Utility functions
│   ├── types.py        # Type definitions
│   └── app.py          # Flask application factory
├── tests/              # Test files
├── data/               # Data storage (history, audio files)
└── config/             # Configuration files
```

## API Endpoints

### Document Scanning & OCR
- `POST /api/capture` - Trigger document scan and OCR processing
- `GET /api/history` - Get all history entries
- `GET /api/history/<id>` - Get specific history entry
- `DELETE /api/history/<id>` - Delete history entry

### Settings & Control
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings (language, speech, audio output)
- `POST /api/stop` - Stop audio playback
- `POST /api/translate` - Translate text between languages
- `GET /api/health` - Health check endpoint

### WebSocket Endpoints
- `WS /ws/audio` - WebSocket audio streaming
- `WS /ws` - WebSocket for blind assistant (object detection streaming)

## Configuration

Settings are stored in `config/settings.json` with the following defaults:
- Language: French
- Speech rate: 1.0×
- Speech pitch: Normal
- Reading mode: Continuous
- Audio output: Pi speaker
- OCR engine: Tesseract
- Camera mode: Phone camera
- Object detection: Enabled

## Blind Assistant Mode

The blind assistant feature uses YOLOv8 nano model for real-time object detection:

```bash
# Run blind assistant server
python blind_assistant_server.py
```

Features:
- Real-time object detection with YOLOv8
- Distance estimation based on object size
- Relevant object filtering (person, chair, car, stairs, etc.)
- Live video preview with annotations
- WebSocket communication for mobile app
- Support for both phone and Pi camera modes
- Audio feedback routing (phone or Pi speaker)

## Hardware Setup

1. Connect Logitech C270 camera to USB port
2. Connect LED ring lighting to GPIO pins
3. Connect speaker to audio jack or GPIO (optional)
4. Ensure camera permissions are granted

## mDNS Setup

To enable `smartreader.local` hostname:

```bash
sudo apt-get install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

Edit `/etc/avahi/avahi-daemon.conf` and set:
```
host-name=smartreader
```

Restart the service:
```bash
sudo systemctl restart avahi-daemon
```
