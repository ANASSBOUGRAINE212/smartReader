# Requirements Document

## Introduction

SmartReader is a mobile companion app for visually impaired users that pairs with a Raspberry Pi 3B device over local Wi-Fi. The app provides a fully voice-navigable interface for document scanning, text-to-speech playback, reading history management, and multi-language settings. The system uses a Logitech C270 camera with LED ring lighting for document capture, OCR engines (Tesseract offline or Google Vision API cloud) for text recognition, and multi-language TTS engines for audio output.

## Glossary

- **Mobile_App**: The React Native application running on iOS (VoiceOver) or Android (TalkBack)
- **Pi_Server**: The Flask REST API server running on Raspberry Pi 3B at port 5000
- **OCR_Engine**: Optical Character Recognition engine (Tesseract or Google Vision API)
- **TTS_Engine**: Text-to-Speech synthesis engine supporting Arabic, French, English, and Darija
- **Voice_Command_Engine**: Speech recognition system for hands-free app control
- **Reading_History**: Persistent storage of past scans with text and audio
- **Screen_Reader**: iOS VoiceOver or Android TalkBack accessibility service
- **WebSocket_Stream**: Real-time audio streaming connection between Pi and mobile app
- **Haptic_Feedback**: Tactile vibration feedback for state changes and confirmations

## Requirements

### Requirement 1: Device Connection and Health Monitoring

**User Story:** As a visually impaired user, I want the app to automatically connect to my Raspberry Pi device and notify me of connection status, so that I know when the system is ready to scan documents.

#### Acceptance Criteria

1. WHEN the Mobile_App starts, THE Mobile_App SHALL attempt to connect to the Pi_Server at http://smartreader.local:5000 or user-configured IP address
2. WHEN the connection is established, THE Mobile_App SHALL provide haptic feedback and announce "Smart Reader connected" via Screen_Reader
3. WHILE the Mobile_App is running, THE Mobile_App SHALL ping the Pi_Server health endpoint every 5 seconds
4. IF the Pi_Server becomes unreachable, THEN THE Mobile_App SHALL provide haptic feedback and announce "Smart Reader is not connected. Please check your Wi-Fi or move closer to the device"
5. WHEN the connection is restored after disconnection, THE Mobile_App SHALL provide haptic feedback and announce "Smart Reader reconnected"

### Requirement 2: Document Scanning and OCR

**User Story:** As a visually impaired user, I want to scan documents using voice commands or a large haptic button, so that I can capture text without needing to see the screen.

#### Acceptance Criteria

1. WHEN a user says "Read document" or activates the scan button, THE Mobile_App SHALL send a POST request to /api/capture on the Pi_Server
2. WHEN the Pi_Server receives the capture request, THE Pi_Server SHALL capture an image using the Logitech C270 camera with LED ring lighting
3. WHEN an image is captured, THE Pi_Server SHALL preprocess the image using OpenCV (deskew and contrast adjustment)
4. WHEN preprocessing is complete, THE Pi_Server SHALL run OCR using the configured OCR_Engine (Tesseract offline or Google Vision API cloud)
5. IF OCR returns no text, THEN THE Mobile_App SHALL announce "No text was detected. Please try repositioning the document and scanning again"
6. WHEN OCR successfully extracts text, THE Pi_Server SHALL generate TTS audio and save the scan to Reading_History
7. WHEN a scan completes successfully, THE Mobile_App SHALL announce "Scan complete. Found N paragraphs of text. Now playing"

### Requirement 3: Text-to-Speech Playback

**User Story:** As a visually impaired user, I want scanned text to be read aloud automatically in my preferred language and voice settings, so that I can immediately hear the document content.

#### Acceptance Criteria

1. WHEN OCR extraction completes, THE Pi_Server SHALL generate TTS audio using the configured TTS_Engine and language settings
2. WHEN TTS audio is generated, THE Pi_Server SHALL stream audio chunks to the Mobile_App via WebSocket_Stream at /ws/audio
3. WHEN the Mobile_App receives audio chunks, THE Mobile_App SHALL play audio through the configured output device (Pi speaker, phone speaker, or Bluetooth headset)
4. WHEN a user says "Stop" or activates the stop button, THE Mobile_App SHALL send a POST request to /api/stop and halt playback immediately
5. IF the WebSocket_Stream drops during playback, THEN THE Mobile_App SHALL automatically retry once, then announce "Audio connection lost. Please try again"
6. WHEN a user says "Repeat last", THE Mobile_App SHALL replay the most recent scan from Reading_History
7. THE TTS_Engine SHALL support Arabic, French, English, and Darija languages

### Requirement 4: Voice Command Recognition

**User Story:** As a visually impaired user, I want to control the app entirely through voice commands, so that I can operate it hands-free without needing to navigate the screen.

#### Acceptance Criteria

1. WHEN the Mobile_App is active, THE Voice_Command_Engine SHALL continuously listen for voice commands
2. WHEN a user says "Read document", THE Mobile_App SHALL trigger a new scan via /api/capture
3. WHEN a user says "Repeat last", THE Mobile_App SHALL replay the most recent scan
4. WHEN a user says "Slower", THE Mobile_App SHALL decrease TTS speech rate via /api/settings
5. WHEN a user says "Faster", THE Mobile_App SHALL increase TTS speech rate via /api/settings
6. WHEN a user says "Translate to [language]" where language is Arabic, French, English, or Darija, THE Mobile_App SHALL switch TTS language via /api/settings
7. WHEN a user says "Stop", THE Mobile_App SHALL halt playback via /api/stop
8. WHEN a user says "Show history", THE Mobile_App SHALL navigate to the History screen
9. WHEN a user says "Share", THE Mobile_App SHALL open the share sheet for the last recognized text
10. WHEN a user says "Search [keyword]", THE Mobile_App SHALL search Reading_History by the spoken keyword
11. WHEN a user says "Delete last", THE Mobile_App SHALL delete the most recent history entry

### Requirement 5: Reading History Management

**User Story:** As a visually impaired user, I want to access my past scans with their audio, so that I can review previously read documents without rescanning them.

#### Acceptance Criteria

1. WHEN a scan completes successfully, THE Pi_Server SHALL save the recognized text, audio file, and metadata to Reading_History
2. WHEN a user navigates to the History screen, THE Mobile_App SHALL retrieve all past scans via GET /api/history
3. WHEN history is loaded, THE Mobile_App SHALL announce "History loaded. N documents found. Say the number of any document to replay it"
4. WHEN displaying a history entry, THE Mobile_App SHALL show an auto-generated title (first 6 words of recognized text) and timestamp
5. WHEN a user selects a history entry, THE Mobile_App SHALL retrieve full text and audio via GET /api/history/<id>
6. WHEN a user swipes to delete or says "Delete last", THE Mobile_App SHALL send DELETE /api/history/<id> and remove the entry
7. WHEN a user searches history by keyword, THE Mobile_App SHALL filter entries containing the keyword and announce results
8. THE Mobile_App SHALL cache the last 20 scans locally for offline access

### Requirement 6: Settings Configuration

**User Story:** As a visually impaired user, I want to customize TTS voice settings, language, and audio output, so that I can personalize the reading experience to my preferences.

#### Acceptance Criteria

1. WHEN a user navigates to the Settings screen, THE Mobile_App SHALL retrieve current settings via GET /api/settings
2. WHEN a user changes any setting, THE Mobile_App SHALL immediately send POST /api/settings to persist the change
3. WHEN a setting is changed, THE Mobile_App SHALL provide haptic feedback and announce the change (e.g., "Language changed to Arabic")
4. THE Mobile_App SHALL support configuring language (Arabic, French, English, Darija) with default French
5. THE Mobile_App SHALL support configuring speech rate from 0.5× to 2.0× with default 1.0×
6. THE Mobile_App SHALL support configuring speech pitch (Low, Normal, High) with default Normal
7. THE Mobile_App SHALL support configuring reading mode (Continuous, Paragraph, Section) with default Continuous
8. THE Mobile_App SHALL support configuring audio output (Pi speaker, Phone, Bluetooth) with default Pi speaker
9. THE Mobile_App SHALL support configuring OCR_Engine (Tesseract offline or Cloud Google Vision) with default Tesseract
10. WHEN Arabic is selected as the language, THE TTS_Engine SHALL ensure correct text direction and pronunciation

### Requirement 7: Content Sharing

**User Story:** As a visually impaired user, I want to share recognized text with family or save it to other apps, so that I can communicate document content or store it for later reference.

#### Acceptance Criteria

1. WHEN a scan completes, THE Mobile_App SHALL enable sharing of the recognized text
2. WHEN a user says "Share" or activates the share button, THE Mobile_App SHALL open the native share sheet
3. THE Mobile_App SHALL support sharing via WhatsApp for medicine instructions or messages
4. THE Mobile_App SHALL support sharing via SMS for addresses, phone numbers, or short notes
5. THE Mobile_App SHALL support sharing via Email for letters or formal documents
6. THE Mobile_App SHALL support copying to Clipboard for pasting into any other app
7. WHEN a share action completes, THE Mobile_App SHALL announce the action (e.g., "Text copied to clipboard" or "Opening WhatsApp")

### Requirement 8: Offline Mode and Synchronization

**User Story:** As a visually impaired user, I want to access my recent reading history even when disconnected from the Pi device, so that I can review documents anywhere.

#### Acceptance Criteria

1. WHEN the Mobile_App is connected, THE Mobile_App SHALL cache the last 20 scans locally
2. WHEN the Pi_Server is unreachable, THE Mobile_App SHALL display and read cached history
3. WHEN offline, THE Mobile_App SHALL announce "Smart Reader is not connected. Showing cached history"
4. WHEN a user attempts to scan while offline, THE Mobile_App SHALL announce "Cannot scan while disconnected. Please reconnect to Smart Reader"
5. WHEN settings are changed while offline, THE Mobile_App SHALL queue the changes locally
6. WHEN the connection is restored, THE Mobile_App SHALL automatically sync queued settings changes to the Pi_Server

### Requirement 9: Screen Reader Accessibility

**User Story:** As a visually impaired user, I want every app interaction to work seamlessly with my screen reader, so that I can navigate and use all features independently.

#### Acceptance Criteria

1. THE Mobile_App SHALL be fully compatible with iOS VoiceOver and Android TalkBack
2. WHEN any UI element receives focus, THE Screen_Reader SHALL announce its purpose and state
3. WHEN any state change occurs, THE Mobile_App SHALL provide both haptic feedback and audio announcement
4. THE Mobile_App SHALL use active, imperative language in all announcements (e.g., "Say 'Read document' to scan")
5. THE Mobile_App SHALL avoid visual metaphors in all announcements (no references to colors, positions, or visual elements)
6. WHEN displaying text on screen, THE Mobile_App SHALL also provide audio confirmation via Screen_Reader
7. THE Mobile_App SHALL keep all announcements to 1-3 sentences maximum
8. THE Mobile_App SHALL ensure all interactive elements have appropriate accessibility labels and hints

### Requirement 10: Error Handling and Recovery

**User Story:** As a visually impaired user, I want clear, actionable error messages when something goes wrong, so that I know what happened and how to fix it.

#### Acceptance Criteria

1. IF the Pi_Server is unreachable, THEN THE Mobile_App SHALL announce "Smart Reader is not connected. Please check your Wi-Fi or move closer to the device" and offer to show cached history
2. IF OCR returns no text, THEN THE Mobile_App SHALL announce "No text was detected. Please try repositioning the document and scanning again"
3. IF TTS fails, THEN THE Mobile_App SHALL offer to display text only and prompt the user to enable Screen_Reader
4. IF the WebSocket_Stream drops mid-playback, THEN THE Mobile_App SHALL automatically retry once, then inform the user
5. WHEN the Pi_Server is unreachable, THE Mobile_App SHALL queue failed requests and retry automatically on reconnection
6. WHEN any error occurs, THE Mobile_App SHALL provide haptic feedback and a concise, actionable error message
7. THE Mobile_App SHALL never over-apologize or use hedging language in error messages

### Requirement 11: Multi-Language Document Detection

**User Story:** As a visually impaired user, I want the app to detect when a document's language differs from my TTS settings, so that I can adjust settings for accurate pronunciation.

#### Acceptance Criteria

1. WHEN OCR extraction completes, THE Pi_Server SHALL attempt to auto-detect the document language
2. IF the detected document language differs from the configured TTS language, THEN THE Mobile_App SHALL announce "Document appears to be in [detected language]. Current TTS language is [configured language]"
3. WHEN a language mismatch is detected, THE Mobile_App SHALL offer to switch TTS language to match the document
4. WHEN a user confirms the language switch, THE Mobile_App SHALL update settings via /api/settings and announce "Language changed to [new language]"

### Requirement 12: Document Translation

**User Story:** As a visually impaired user, I want to translate scanned documents from one language to another, so that I can understand content written in languages I don't speak.

#### Acceptance Criteria

1. WHEN a scan completes with recognized text, THE Mobile_App SHALL enable translation functionality
2. WHEN a user says "Translate to [language]" where language is Arabic, French, English, or Darija, THE Mobile_App SHALL send the recognized text to a translation service
3. WHEN translation completes, THE Mobile_App SHALL announce "Translation complete" and play the translated text using the target language TTS_Engine
4. WHEN a user requests translation, THE Mobile_App SHALL preserve the original text and audio in Reading_History
5. WHEN a translated document is saved, THE Mobile_App SHALL store both original and translated versions with clear labels
6. IF translation fails due to network issues, THEN THE Mobile_App SHALL announce "Translation unavailable. Please check your internet connection"
7. WHEN displaying a translated document in history, THE Mobile_App SHALL announce "Original language: [source], Translated to: [target]"
8. THE Mobile_App SHALL support translation between any combination of Arabic, French, English, and Darija

### Requirement 13: Home Screen Interface

**User Story:** As a visually impaired user, I want a simple home screen with large, haptic-enabled controls, so that I can easily trigger scans and control playback.

#### Acceptance Criteria

1. THE Home screen SHALL contain a large haptic scan button as the primary control
2. THE Home screen SHALL display connection status (connected/disconnected) updated every 5 seconds
3. THE Home screen SHALL provide a Stop button for halting playback
4. THE Home screen SHALL provide a Repeat button for replaying the last scan
5. WHEN a scan completes, THE Home screen SHALL display the recognized text
6. WHEN the scan button is activated, THE Mobile_App SHALL provide haptic feedback
7. WHEN the Stop button is activated, THE Mobile_App SHALL provide haptic feedback and halt playback immediately
8. WHEN the Repeat button is activated, THE Mobile_App SHALL provide haptic feedback and replay the last scan
