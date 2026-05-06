# SmartReader - Mobile App for Visually Impaired Users

SmartReader is a comprehensive mobile application system designed for visually impaired users to scan documents, extract text via OCR, and receive audio feedback through text-to-speech synthesis. The system consists of a React Native mobile app and a Flask-based Raspberry Pi server.

## System Overview

### Mobile App (React Native + TypeScript)
- Voice-first interface with full accessibility support
- Document scanning control
- Text-to-speech playback
- Reading history management
- Offline mode with local caching
- Multi-language support (Arabic, French, English, Darija)
- Translation functionality

### Pi Server (Flask + Python)
- REST API for mobile communication
- WebSocket audio streaming
- Camera control and image preprocessing
- OCR with Tesseract and Google Vision API
- Multi-language TTS synthesis
- Translation service
- History and settings persistence

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Mobile App        │         │   Raspberry Pi       │
│   (React Native)    │◄───────►│   (Flask Server)     │
│                     │  REST   │                      │
│  - Voice Commands   │  API    │  - Camera Control    │
│  - Audio Playback   │         │  - OCR Processing    │
│  - History Cache    │  WebSocket  - TTS Synthesis  │
│  - Settings UI      │◄───────►│  - History Storage   │
└─────────────────────┘  Audio  └──────────────────────┘
                         Stream           │
                                         │
                                    ┌────▼─────┐
                                    │ Hardware │
                                    │ - Camera │
                                    │ - LED    │
                                    │ - Speaker│
                                    └──────────┘
```

## Quick Start

### Mobile App

```bash
cd smartreader-mobile
npm install
npx expo start
```

### Pi Server

```bash
cd pi-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

## Documentation

- [Mobile App README](smartreader-mobile/README.md)
- [Pi Server README](pi-server/README.md)
- [Requirements Document](.kiro/specs/smartreader-mobile-app/requirements.md)
- [Design Document](.kiro/specs/smartreader-mobile-app/design.md)
- [Implementation Tasks](.kiro/specs/smartreader-mobile-app/tasks.md)

## Key Features

### Accessibility First
- Full VoiceOver (iOS) and TalkBack (Android) support
- Haptic feedback for all interactions
- Voice command control
- Screen reader-friendly announcements
- No visual metaphors

### Multi-Language Support
- Arabic, French, English, Darija
- Language detection
- Translation between supported languages
- Language-specific TTS pronunciation

### Offline Capability
- Local caching of last 20 scans
- Offline history access
- Settings queue and sync on reconnection

### Smart Features
- Auto-title generation (first 6 words)
- Paragraph counting
- Reading mode options (continuous, paragraph, section)
- Configurable speech rate and pitch
- Multiple audio output options

## Testing

Both projects include comprehensive testing:
- Unit tests for individual components
- Property-based tests for universal correctness
- Integration tests for end-to-end workflows

### Mobile App Testing
```bash
cd mobile-app
npm test
```

### Pi Server Testing
```bash
cd pi-server
pytest
```

## Requirements

### Mobile App
- Node.js 18+
- React Native development environment
- iOS Simulator or Android Studio

### Pi Server
- Raspberry Pi 3B
- Python 3.9+
- Logitech C270 camera
- Tesseract OCR
- Optional: GPIO speaker

## License

Copyright © 2024 SmartReader Project

## Contributing

This project follows strict accessibility guidelines. All contributions must:
- Maintain full screen reader compatibility
- Include haptic feedback for state changes
- Use active, imperative language in announcements
- Avoid visual metaphors
- Include comprehensive tests
