# SmartReader - Assistive Reading & Navigation System

A comprehensive assistive technology solution combining document scanning, OCR, text-to-speech, and real-time object detection to help visually impaired users read documents and navigate their environment.

![Blind Assistant Demo](result(blind%20assistant).png)

## Overview

SmartReader is a dual-component system consisting of:
- **Mobile App**: React Native/Expo mobile application for document scanning and blind assistance
- **Pi Server**: Raspberry Pi-based backend server for OCR processing, TTS, and object detection

## Key Features

### Document Reading
- **Camera-based Scanning**: Capture documents using phone or Pi camera
- **Dual OCR Engines**: Offline processing with Tesseract or cloud-based with Google Vision API
- **Multi-language Support**: Arabic, French, English, and Darija
- **Text-to-Speech**: Natural-sounding voice output with adjustable rate and pitch
- **Translation**: Translate extracted text between supported languages
- **Reading History**: Save and manage previously scanned documents

### Blind Assistant (Navigation Aid)
- **Real-time Object Detection**: YOLOv8-based detection of relevant objects
- **Distance Estimation**: Proximity alerts based on object size
- **Relevant Object Filtering**: Focus on important objects (people, chairs, stairs, doors, vehicles, etc.)
- **Audio Feedback**: Spoken descriptions of detected objects and their distances
- **Live Video Preview**: Annotated video stream with bounding boxes
- **Dual Camera Support**: Switch between phone camera and Raspberry Pi camera

### Technical Highlights
- **WebSocket Communication**: Real-time streaming for audio and video
- **Flexible Audio Routing**: Output to phone speaker or Pi-connected speaker
- **Persistent Storage**: Local history and settings management
- **mDNS Discovery**: Easy connection via `smartreader.local` hostname
- **Modular Architecture**: Clean separation between mobile app and server

## System Architecture

```
┌─────────────────────────┐
│   Mobile App (Expo)     │
│  - Document Scanner     │
│  - Blind Assistant UI   │
│  - Settings & History   │
└───────────┬─────────────┘
            │
            │ REST API / WebSocket
            │
┌───────────▼─────────────┐
│  Raspberry Pi Server    │
│  - Flask REST API       │
│  - OCR Processing       │
│  - TTS Engine           │
│  - YOLOv8 Detection     │
│  - Camera Control       │
└─────────────────────────┘
```

## Project Structure

```
smartreader/
├── pi-server/                    # Raspberry Pi backend server
│   ├── src/                      # Flask application source
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helper functions
│   ├── blind_assistant_server.py # Object detection server
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Server documentation
│
├── smartreader-mobile-clean/    # Mobile application
│   ├── app/                     # Expo Router screens
│   ├── components/              # React components
│   ├── src/                     # Services and stores
│   ├── package.json             # Node dependencies
│   └── README.md                # App documentation
│
└── README.md                    # This file
```

## Quick Start

### 1. Set Up Raspberry Pi Server

```bash
cd pi-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ara tesseract-ocr-fra

# Run main server
python src/app.py

# Run blind assistant server (in another terminal)
python blind_assistant_server.py
```

### 2. Set Up Mobile App

```bash
cd smartreader-mobile-clean

# Install dependencies
npm install

# Start development server
npx expo start

# Run on device or emulator
npm run android  # or npm run ios
```

### 3. Configure Connection

Update the server URL in the mobile app to point to your Raspberry Pi:
- Default: `http://smartreader.local:5000` (main server)
- Blind Assistant: `ws://smartreader.local:8000/ws` (WebSocket)

## Hardware Requirements

### Raspberry Pi Setup
- Raspberry Pi 3B or 4
- Logitech C270 USB camera with LED ring lighting
- MicroSD card (16GB+ recommended)
- Power supply (5V 3A recommended)
- Optional: GPIO-connected speaker for audio output
- Optional: Pi Camera Module v2 (for native camera support)

### Mobile Device
- iOS 13+ or Android 8+
- Camera with autofocus
- Stable WiFi connection to Pi server

## Use Cases

1. **Document Reading**: Scan books, letters, labels, or any printed text and have it read aloud
2. **Navigation Assistance**: Real-time object detection helps users navigate indoor/outdoor spaces
3. **Label Recognition**: Identify products, signs, and labels in daily life
4. **Educational Support**: Access printed educational materials independently
5. **Daily Living**: Read recipes, instructions, medication labels, etc.

## Technologies Used

### Backend (Pi Server)
- Python 3.9+
- Flask (REST API)
- FastAPI (WebSocket server)
- Tesseract OCR
- Google Vision API
- gTTS / pyttsx3 (Text-to-Speech)
- OpenCV (Image processing)
- YOLOv8 (Object detection)
- picamera2 (Pi camera support)

### Frontend (Mobile App)
- React Native
- Expo SDK 54
- TypeScript
- Expo Camera
- Expo Speech
- Socket.io Client
- Zustand (State management)
- React Navigation

## Performance

- **OCR Processing**: 2-5 seconds per document (Tesseract), 1-3 seconds (Google Vision)
- **Object Detection**: 15-20 FPS on Raspberry Pi 4, 8-12 FPS on Pi 3B
- **TTS Latency**: Near real-time with streaming audio
- **WebSocket Latency**: <100ms on local network

## Future Enhancements

- Offline translation support
- Face recognition for identifying people
- Text recognition in natural scenes (street signs, menus)
- Barcode/QR code scanning
- Voice commands for hands-free operation
- Cloud sync for reading history
- Multi-user support with profiles

## Acknowledgments

- **Team Members**: 
  - [Ibtissame](https://github.com/ibtissame123)
  - [Hiba Nahri](https://github.com/hibanahri)
- **ENSA Tétouan**: Our teachers and institution for providing the Raspberry Pi hardware and support
- **Nexus Club**: For their guidance and resources throughout the project
- **Open Source Community**:
  - YOLOv8 by Ultralytics for object detection
  - Tesseract OCR by Google
  - Expo team for the excellent mobile development framework
  - Various libraries and tools that made this project possible

---

**Note**: This system is designed to assist visually impaired users but should not replace professional mobility training or other assistive devices. Always prioritize safety when navigating.
