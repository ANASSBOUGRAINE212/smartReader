# Implementation Plan: SmartReader Mobile App

## Overview

This implementation plan breaks down the SmartReader Mobile App into discrete coding tasks. The system consists of a React Native mobile application (TypeScript) and a Flask-based Raspberry Pi server (Python). Tasks are organized to build incrementally, with testing integrated throughout to validate correctness early.

## Tasks

- [ ] 1. Set up project structure and development environment
  - Create React Native project with TypeScript configuration
  - Create Flask project structure for Pi server
  - Set up testing frameworks (Jest for mobile, pytest for Pi)
  - Configure fast-check for property-based testing
  - Set up ESLint, Prettier, and type checking
  - Create shared type definitions for API contracts
  - _Requirements: All_

- [ ] 2. Implement Pi Server core infrastructure
  - [ ] 2.1 Create Flask application with REST API endpoints skeleton
    - Implement /api/capture, /api/history, /api/settings, /api/stop, /api/translate, /api/health endpoints
    - Set up request/response JSON serialization
    - Configure CORS for mobile app access
    - _Requirements: 1.1, 2.1, 5.2, 6.1, 10.1_

  - [ ]* 2.2 Write unit tests for API endpoints
    - Test endpoint routing and response formats
    - Test error handling for invalid requests
    - _Requirements: 1.1, 2.1, 5.2, 6.1_

  - [ ] 2.3 Implement WebSocket server for audio streaming
    - Create WebSocket endpoint at /ws/audio
    - Implement connection management and client tracking
    - Add audio chunk streaming functionality
    - _Requirements: 3.2_

  - [ ]* 2.4 Write unit tests for WebSocket server
    - Test connection establishment and disconnection
    - Test audio chunk streaming
    - _Requirements: 3.2_

- [ ] 3. Implement Pi Server camera and OCR pipeline
  - [ ] 3.1 Create CaptureService for camera control
    - Implement camera initialization and image capture
    - Add LED ring lighting control
    - Implement OpenCV preprocessing (deskew, contrast adjustment)
    - _Requirements: 2.2, 2.3_

  - [ ]* 3.2 Write unit tests for CaptureService
    - Test image capture with mocked camera
    - Test preprocessing transformations
    - _Requirements: 2.2, 2.3_

  - [ ]* 3.3 Write property test for image preprocessing
    - **Property 4: Image preprocessing is applied**
    - **Validates: Requirements 2.3**

  - [ ] 3.4 Create OCRService for text extraction
    - Implement Tesseract OCR integration (offline)
    - Implement Google Vision API integration (cloud)
    - Add language detection functionality
    - Add paragraph counting
    - _Requirements: 2.4, 11.1_

  - [ ]* 3.5 Write unit tests for OCRService
    - Test Tesseract extraction with sample images
    - Test Google Vision extraction with mocked API
    - Test language detection
    - Test empty text handling
    - _Requirements: 2.4, 2.5, 11.1_

  - [ ]* 3.6 Write property test for OCR engine selection
    - **Property 5: OCR engine selection**
    - **Validates: Requirements 2.4**

- [ ] 4. Implement Pi Server TTS and translation services
  - [ ] 4.1 Create TTSService for speech synthesis
    - Implement Coqui TTS integration
    - Implement Google TTS integration as fallback
    - Support Arabic, French, English, Darija languages
    - Apply speech rate and pitch settings
    - _Requirements: 3.1, 6.4_

  - [ ]* 4.2 Write unit tests for TTSService
    - Test audio generation for each language
    - Test speech rate and pitch adjustments
    - Test error handling for TTS failures
    - _Requirements: 3.1, 6.4_

  - [ ]* 4.3 Write property test for TTS settings
    - **Property 8: TTS uses configured settings**
    - **Validates: Requirements 3.1**

  - [ ] 4.4 Create TranslationService for text translation
    - Integrate translation API (Google Translate or similar)
    - Support translation between Arabic, French, English, Darija
    - Handle translation errors gracefully
    - _Requirements: 12.2_

  - [ ]* 4.5 Write unit tests for TranslationService
    - Test translation for all language pairs
    - Test error handling for API failures
    - _Requirements: 12.2, 12.6_

  - [ ]* 4.6 Write property test for translation requests
    - **Property 50: Translation request sent**
    - **Validates: Requirements 12.2**

- [ ] 5. Implement Pi Server history and settings management
  - [ ] 5.1 Create HistoryService for scan persistence
    - Implement save_scan with file storage
    - Generate auto-titles (first 6 words)
    - Implement get_all, get_by_id, delete methods
    - Store audio files and metadata
    - _Requirements: 2.6, 5.1, 5.4_

  - [ ]* 5.2 Write unit tests for HistoryService
    - Test scan saving and retrieval
    - Test title generation with various text lengths
    - Test deletion
    - _Requirements: 2.6, 5.1, 5.4_

  - [ ]* 5.3 Write property test for title generation
    - **Property 21: History title generation**
    - **Validates: Requirements 5.4**

  - [ ] 5.4 Create SettingsService for configuration management
    - Implement load_settings and save_settings
    - Provide default values
    - Validate setting values
    - _Requirements: 6.1, 6.2_

  - [ ]* 5.5 Write unit tests for SettingsService
    - Test settings persistence
    - Test default values
    - Test validation
    - _Requirements: 6.1, 6.2, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [ ]* 5.6 Write property test for speech rate validation
    - **Property 29: Speech rate validation**
    - **Validates: Requirements 6.5**

- [ ] 6. Wire Pi Server components and implement scan workflow
  - [ ] 6.1 Implement POST /api/capture endpoint handler
    - Call CaptureService to capture and preprocess image
    - Call OCRService to extract text
    - Call TTSService to generate audio
    - Call HistoryService to save scan
    - Stream audio via WebSocket
    - Return scan result JSON
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 3.1, 3.2_

  - [ ]* 6.2 Write integration test for scan workflow
    - Test end-to-end scan from capture to audio streaming
    - Test error handling at each stage
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 3.1, 3.2_

  - [ ]* 6.3 Write property test for scan persistence
    - **Property 6: Successful scan persistence**
    - **Validates: Requirements 2.6, 5.1**

  - [ ] 6.2 Implement remaining API endpoint handlers
    - GET /api/history: retrieve all history entries
    - GET /api/history/<id>: retrieve specific entry
    - DELETE /api/history/<id>: delete entry
    - GET /api/settings: retrieve settings
    - POST /api/settings: update settings
    - POST /api/stop: stop audio playback
    - POST /api/translate: translate text
    - GET /api/health: health check
    - _Requirements: 5.2, 5.5, 5.6, 6.1, 6.2, 3.4, 12.2, 1.3_

  - [ ]* 6.3 Write integration tests for API endpoints
    - Test each endpoint with valid and invalid inputs
    - Test error responses
    - _Requirements: 5.2, 5.5, 5.6, 6.1, 6.2, 3.4, 12.2, 1.3_

- [ ] 7. Checkpoint - Ensure Pi Server tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement mobile app state management
  - [ ] 8.1 Set up Zustand store with state slices
    - Create connection state slice
    - Create scan state slice
    - Create history state slice
    - Create settings state slice
    - Create voice command state slice
    - _Requirements: All_

  - [ ]* 8.2 Write unit tests for state management
    - Test state updates and selectors
    - Test state persistence
    - _Requirements: All_

- [ ] 9. Implement mobile app connection management
  - [ ] 9.1 Create ConnectionManager component
    - Implement connect/disconnect methods
    - Implement health check polling (5-second interval)
    - Emit connection status changes
    - Handle reconnection logic
    - Queue failed requests for retry
    - _Requirements: 1.1, 1.3, 10.5_

  - [ ]* 9.2 Write unit tests for ConnectionManager
    - Test connection establishment
    - Test health check polling
    - Test reconnection logic
    - Test request queueing
    - _Requirements: 1.1, 1.3, 10.5_

  - [ ]* 9.3 Write property test for health check interval
    - **Property 2: Health check polling interval**
    - **Validates: Requirements 1.3**

  - [ ]* 9.4 Write property test for connection feedback
    - **Property 1: Connection state changes produce feedback**
    - **Validates: Requirements 1.2, 1.4, 1.5**

  - [ ]* 9.5 Write property test for failed request queueing
    - **Property 43: Failed request queueing**
    - **Validates: Requirements 10.5**

- [ ] 10. Implement mobile app voice command engine
  - [ ] 10.1 Create VoiceCommandEngine component
    - Integrate react-native-voice
    - Implement continuous listening
    - Parse voice commands into structured objects
    - Handle recognition errors
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11_

  - [ ]* 10.2 Write unit tests for VoiceCommandEngine
    - Test command parsing for all command types
    - Test error handling
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11_

  - [ ]* 10.3 Write property tests for voice commands
    - **Property 13: Voice command speed adjustment**
    - **Property 14: Voice command language switching**
    - **Property 15: Voice command navigation**
    - **Property 16: Voice command share**
    - **Property 17: Voice command search**
    - **Property 18: Voice command delete**
    - **Validates: Requirements 4.4, 4.5, 4.6, 4.8, 4.9, 4.10, 4.11**

- [ ] 11. Implement mobile app scan controller
  - [ ] 11.1 Create ScanController component
    - Implement triggerScan method (POST /api/capture)
    - Implement stopPlayback method (POST /api/stop)
    - Implement repeatLast method
    - Handle scan results and errors
    - Update history state
    - _Requirements: 2.1, 3.4, 3.6_

  - [ ]* 11.2 Write unit tests for ScanController
    - Test scan triggering
    - Test stop playback
    - Test repeat last
    - Test error handling
    - _Requirements: 2.1, 3.4, 3.6_

  - [ ]* 11.3 Write property tests for scan operations
    - **Property 3: Scan triggers API call**
    - **Property 11: Stop command halts playback**
    - **Property 12: Repeat command replays last scan**
    - **Validates: Requirements 2.1, 3.4, 3.6**

- [ ] 12. Implement mobile app audio player
  - [ ] 12.1 Create AudioPlayer component
    - Implement WebSocket connection for audio streaming
    - Implement audio buffering and playback
    - Implement stop functionality
    - Handle audio output routing (Pi speaker, phone, Bluetooth)
    - Implement automatic retry on stream failure
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 6.8_

  - [ ]* 12.2 Write unit tests for AudioPlayer
    - Test WebSocket connection
    - Test audio playback
    - Test output routing
    - Test retry logic
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 6.8_

  - [ ]* 12.3 Write property tests for audio operations
    - **Property 9: Audio streaming via WebSocket**
    - **Property 10: Audio output routing**
    - **Validates: Requirements 3.2, 3.3**

- [ ] 13. Implement mobile app history manager
  - [ ] 13.1 Create HistoryManager component
    - Implement fetchHistory (GET /api/history)
    - Implement getEntry (GET /api/history/<id>)
    - Implement deleteEntry (DELETE /api/history/<id>)
    - Implement searchHistory with keyword filtering
    - Implement local caching (last 20 entries)
    - Implement offline access to cached entries
    - _Requirements: 5.2, 5.5, 5.6, 5.7, 5.8, 8.1, 8.2_

  - [ ]* 13.2 Write unit tests for HistoryManager
    - Test history fetching
    - Test entry retrieval
    - Test entry deletion
    - Test search filtering
    - Test caching
    - Test offline access
    - _Requirements: 5.2, 5.5, 5.6, 5.7, 5.8, 8.1, 8.2_

  - [ ]* 13.3 Write property tests for history operations
    - **Property 19: History retrieval on navigation**
    - **Property 22: History entry selection**
    - **Property 23: History entry deletion**
    - **Property 24: History search filtering**
    - **Property 25: Cache size limit**
    - **Property 33: Offline cached history access**
    - **Validates: Requirements 5.2, 5.5, 5.6, 5.7, 5.8, 8.2**

- [ ] 14. Implement mobile app settings manager
  - [ ] 14.1 Create SettingsManager component
    - Implement getSettings (GET /api/settings)
    - Implement updateSetting (POST /api/settings)
    - Implement offline settings queueing
    - Implement syncQueuedUpdates on reconnection
    - Validate setting values
    - _Requirements: 6.1, 6.2, 6.5, 8.5, 8.6_

  - [ ]* 14.2 Write unit tests for SettingsManager
    - Test settings retrieval
    - Test settings updates
    - Test offline queueing
    - Test sync on reconnection
    - Test validation
    - _Requirements: 6.1, 6.2, 6.5, 8.5, 8.6_

  - [ ]* 14.3 Write property tests for settings operations
    - **Property 26: Settings retrieval on navigation**
    - **Property 27: Settings persistence**
    - **Property 28: Settings change feedback**
    - **Property 35: Offline settings queueing**
    - **Property 36: Settings sync on reconnection**
    - **Validates: Requirements 6.1, 6.2, 6.3, 8.5, 8.6**

- [ ] 15. Implement mobile app sharing functionality
  - [ ] 15.1 Create ShareManager component
    - Implement share method with native share sheet
    - Implement copyToClipboard method
    - _Requirements: 7.2, 7.6_

  - [ ]* 15.2 Write unit tests for ShareManager
    - Test share sheet opening
    - Test clipboard copy
    - _Requirements: 7.2, 7.6_

  - [ ]* 15.3 Write property tests for sharing operations
    - **Property 30: Share action opens share sheet**
    - **Property 31: Clipboard copy**
    - **Property 32: Share action announcement**
    - **Validates: Requirements 7.2, 7.6, 7.7**

- [ ] 16. Implement mobile app accessibility manager
  - [ ] 16.1 Create AccessibilityManager component
    - Implement announce method for screen reader
    - Implement provideHapticFeedback method
    - Implement isScreenReaderEnabled check
    - Format messages for accessibility
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [ ]* 16.2 Write unit tests for AccessibilityManager
    - Test announcements
    - Test haptic feedback
    - Test screen reader detection
    - Test message formatting
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [ ]* 16.3 Write property tests for accessibility
    - **Property 37: Interactive elements have accessibility labels**
    - **Property 38: State changes produce feedback**
    - **Property 39: Announcements use active voice**
    - **Property 40: Announcements avoid visual metaphors**
    - **Property 41: Text display includes audio**
    - **Property 42: Announcement length limit**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**

- [ ] 17. Checkpoint - Ensure mobile app component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Implement Home screen UI
  - [ ] 18.1 Create Home screen component
    - Add large haptic scan button
    - Display connection status badge
    - Add Stop button
    - Add Repeat button
    - Display recognized text after scan
    - Integrate with ScanController, AudioPlayer, AccessibilityManager
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [ ]* 18.2 Write unit tests for Home screen
    - Test button interactions
    - Test status display
    - Test text display
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [ ]* 18.3 Write property tests for Home screen
    - **Property 55: Scan result display**
    - **Property 56: Button activation feedback**
    - **Validates: Requirements 13.5, 13.6**

- [ ] 19. Implement History screen UI
  - [ ] 19.1 Create History screen component
    - Display list of history entries with titles and timestamps
    - Implement entry selection for replay
    - Implement swipe-to-delete
    - Implement voice search
    - Integrate with HistoryManager, AudioPlayer, AccessibilityManager
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [ ]* 19.2 Write unit tests for History screen
    - Test entry list display
    - Test entry selection
    - Test deletion
    - Test search
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [ ]* 19.3 Write property test for history announcements
    - **Property 20: History load announcement**
    - **Validates: Requirements 5.3**

- [ ] 20. Implement Settings screen UI
  - [ ] 20.1 Create Settings screen component
    - Add language selector (Arabic, French, English, Darija)
    - Add speech rate slider (0.5× - 2.0×)
    - Add speech pitch selector (Low, Normal, High)
    - Add reading mode selector (Continuous, Paragraph, Section)
    - Add audio output selector (Pi speaker, Phone, Bluetooth)
    - Add OCR engine selector (Tesseract, Cloud)
    - Integrate with SettingsManager, AccessibilityManager
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [ ]* 20.2 Write unit tests for Settings screen
    - Test setting controls
    - Test setting updates
    - Test feedback
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

- [ ] 21. Implement translation functionality
  - [ ] 21.1 Add translation UI to Home and History screens
    - Add "Translate" button/voice command handler
    - Display translation results
    - Show original and translated versions in history
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.7_

  - [ ]* 21.2 Write unit tests for translation UI
    - Test translation triggering
    - Test result display
    - Test history display with translations
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.7_

  - [ ]* 21.3 Write property tests for translation
    - **Property 51: Translation completion announcement**
    - **Property 52: Translation preserves original**
    - **Property 53: Translation storage**
    - **Property 54: Translated document announcement**
    - **Validates: Requirements 12.3, 12.4, 12.5, 12.7**

- [ ] 22. Implement language detection and mismatch handling
  - [ ] 22.1 Add language detection to scan workflow
    - Display language mismatch notification
    - Offer language switch option
    - Update settings on confirmation
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ]* 22.2 Write unit tests for language detection
    - Test mismatch detection
    - Test notification display
    - Test language switch
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ]* 22.3 Write property tests for language detection
    - **Property 46: Language detection attempted**
    - **Property 47: Language mismatch announcement**
    - **Property 48: Language mismatch offers switch**
    - **Property 49: Language switch confirmation**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**

- [ ] 23. Implement error handling and announcements
  - [ ] 23.1 Add error handling to all components
    - Implement error announcements for all error types
    - Add haptic feedback for errors
    - Implement recovery actions
    - Ensure error messages follow style guidelines (concise, actionable, no apologies)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [ ]* 23.2 Write unit tests for error handling
    - Test error detection
    - Test error announcements
    - Test recovery actions
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [ ]* 23.3 Write property tests for error handling
    - **Property 44: Error feedback**
    - **Property 45: Error messages avoid apologetic language**
    - **Validates: Requirements 10.6, 10.7**

- [ ] 24. Implement offline mode
  - [ ] 24.1 Add offline detection and announcements
    - Detect offline state
    - Announce offline status
    - Show cached history
    - Prevent scan attempts while offline
    - _Requirements: 8.2, 8.3, 8.4_

  - [ ]* 24.2 Write unit tests for offline mode
    - Test offline detection
    - Test offline announcements
    - Test cached history access
    - Test scan prevention
    - _Requirements: 8.2, 8.3, 8.4_

  - [ ]* 24.3 Write property test for offline announcements
    - **Property 34: Offline announcement**
    - **Validates: Requirements 8.3**

- [ ] 25. Implement scan completion announcements
  - [ ] 25.1 Add announcement logic to scan workflow
    - Announce scan completion with paragraph count
    - Announce "Now playing" when audio starts
    - _Requirements: 2.7_

  - [ ]* 25.2 Write property test for scan announcements
    - **Property 7: Scan completion announcement**
    - **Validates: Requirements 2.7**

- [ ] 26. Final integration and end-to-end testing
  - [ ]* 26.1 Write end-to-end integration tests
    - Test complete scan workflow: trigger → capture → OCR → TTS → playback
    - Test complete history workflow: scan → save → retrieve → replay → delete
    - Test complete settings workflow: change → persist → retrieve → apply
    - Test complete translation workflow: scan → translate → save → replay
    - Test complete offline workflow: disconnect → queue → reconnect → sync
    - Test complete voice command workflow: recognize → parse → execute → feedback
    - _Requirements: All_

  - [ ] 26.2 Test with real Raspberry Pi hardware
    - Test camera capture and LED lighting
    - Test OCR with real documents
    - Test TTS audio output
    - Test WebSocket audio streaming
    - Test all API endpoints
    - _Requirements: All_

  - [ ] 26.3 Test with real mobile devices
    - Test on iOS with VoiceOver
    - Test on Android with TalkBack
    - Test voice commands
    - Test haptic feedback
    - Test all screens and workflows
    - _Requirements: All_

- [ ] 27. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The mobile app uses TypeScript with React Native
- The Pi server uses Python with Flask
- Testing uses Jest and fast-check for mobile, pytest for Pi server
