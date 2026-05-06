# Design Document

## Overview

SmartReader is a distributed mobile application system consisting of a React Native mobile app and a Flask-based Raspberry Pi server. The system enables visually impaired users to scan documents, extract text via OCR, and receive audio feedback through text-to-speech synthesis. The architecture prioritizes accessibility, offline capability, and voice-first interaction.

The mobile app communicates with the Pi server over local Wi-Fi using REST APIs for control operations and WebSocket for real-time audio streaming. The system supports multiple languages (Arabic, French, English, Darija) and provides comprehensive voice command control for hands-free operation.

## Architecture

### System Components

The system follows a client-server architecture with three primary layers:

**Mobile Application Layer (React Native)**
- Cross-platform mobile app (iOS and Android)
- Voice command recognition engine
- State management (Zustand)
- Local caching and offline storage
- Screen reader integration (VoiceOver/TalkBack)
- Audio playback and haptic feedback

**Pi Server Layer (Flask on Raspberry Pi 3B)**
- REST API server (Flask)
- WebSocket server for audio streaming
- OCR pipeline (OpenCV preprocessing + Tesseract/Google Vision)
- TTS synthesis (Coqui/Google TTS)
- Document history storage
- Settings persistence

**Hardware Layer**
- Logitech C270 camera with LED ring lighting
- GPIO-connected speaker
- Optional Bluetooth audio output

### Communication Protocols

**REST API**: Used for control operations (scan, settings, history management)
- Base URL: `http://smartreader.local:5000` (mDNS) or user-configured IP
- JSON request/response format
- Health check polling every 5 seconds

**WebSocket**: Used for real-time audio streaming
- Endpoint: `ws://smartreader.local:5000/ws/audio`
- Binary audio chunk streaming
- Automatic reconnection on disconnect

**mDNS**: Device discovery using `smartreader.local` hostname
- Fallback to manual IP configuration
- Connection status monitoring

## Components and Interfaces

### Mobile App Components

#### ConnectionManager
Manages Pi server connectivity and health monitoring.

**Interface:**
```typescript
interface ConnectionManager {
  connect(hostname: string): Promise<ConnectionStatus>
  disconnect(): void
  getStatus(): ConnectionStatus
  onStatusChange(callback: (status: ConnectionStatus) => void): void
  ping(): Promise<boolean>
}

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting'
```

**Responsibilities:**
- Establish and maintain connection to Pi server
- Poll health endpoint every 5 seconds
- Emit connection status changes
- Handle reconnection logic
- Queue failed requests for retry

#### VoiceCommandEngine
Processes voice commands and maps them to app actions.

**Interface:**
```typescript
interface VoiceCommandEngine {
  start(): void
  stop(): void
  onCommand(callback: (command: VoiceCommand) => void): void
}

type VoiceCommand = 
  | { type: 'scan' }
  | { type: 'repeat' }
  | { type: 'stop' }
  | { type: 'speed', direction: 'faster' | 'slower' }
  | { type: 'translate', language: Language }
  | { type: 'history' }
  | { type: 'share' }
  | { type: 'search', keyword: string }
  | { type: 'delete' }

type Language = 'arabic' | 'french' | 'english' | 'darija'
```

**Responsibilities:**
- Continuous voice recognition using react-native-voice
- Command parsing and validation
- Emit structured command objects
- Handle recognition errors

#### ScanController
Orchestrates document scanning workflow.

**Interface:**
```typescript
interface ScanController {
  triggerScan(): Promise<ScanResult>
  stopPlayback(): Promise<void>
  repeatLast(): Promise<void>
}

interface ScanResult {
  id: string
  text: string
  audioUrl: string
  timestamp: Date
  language: Language
  paragraphCount: number
}
```

**Responsibilities:**
- Send scan requests to Pi server
- Receive and process scan results
- Coordinate audio playback
- Update reading history
- Handle scan errors

#### AudioPlayer
Manages audio playback from WebSocket stream or cached files.

**Interface:**
```typescript
interface AudioPlayer {
  playStream(websocketUrl: string): Promise<void>
  playFile(audioUrl: string): Promise<void>
  stop(): void
  setOutput(output: AudioOutput): void
  onPlaybackComplete(callback: () => void): void
}

type AudioOutput = 'pi-speaker' | 'phone' | 'bluetooth'
```

**Responsibilities:**
- Connect to WebSocket audio stream
- Buffer and play audio chunks
- Handle playback interruptions
- Manage audio output routing
- Automatic retry on stream failure

#### HistoryManager
Manages reading history storage and retrieval.

**Interface:**
```typescript
interface HistoryManager {
  fetchHistory(): Promise<HistoryEntry[]>
  getEntry(id: string): Promise<HistoryEntry>
  deleteEntry(id: string): Promise<void>
  searchHistory(keyword: string): HistoryEntry[]
  cacheEntries(entries: HistoryEntry[]): void
  getCachedHistory(): HistoryEntry[]
}

interface HistoryEntry {
  id: string
  title: string
  text: string
  audioUrl: string
  timestamp: Date
  language: Language
  translated?: {
    targetLanguage: Language
    text: string
    audioUrl: string
  }
}
```

**Responsibilities:**
- Fetch history from Pi server
- Cache last 20 entries locally
- Provide offline access to cached entries
- Search and filter history
- Delete entries from server and cache

#### SettingsManager
Manages app and TTS configuration.

**Interface:**
```typescript
interface SettingsManager {
  getSettings(): Promise<Settings>
  updateSetting<K extends keyof Settings>(
    key: K,
    value: Settings[K]
  ): Promise<void>
  queueOfflineUpdate(key: string, value: any): void
  syncQueuedUpdates(): Promise<void>
}

interface Settings {
  language: Language
  speechRate: number // 0.5 - 2.0
  speechPitch: 'low' | 'normal' | 'high'
  readingMode: 'continuous' | 'paragraph' | 'section'
  audioOutput: AudioOutput
  ocrEngine: 'tesseract' | 'cloud'
}
```

**Responsibilities:**
- Fetch settings from Pi server
- Update settings and persist to server
- Queue settings changes when offline
- Sync queued changes on reconnection
- Validate setting values

#### ShareManager
Handles content sharing to external apps.

**Interface:**
```typescript
interface ShareManager {
  share(text: string, options?: ShareOptions): Promise<void>
  copyToClipboard(text: string): Promise<void>
}

interface ShareOptions {
  title?: string
  dialogTitle?: string
}
```

**Responsibilities:**
- Open native share sheet
- Copy text to clipboard
- Announce share actions via screen reader

#### AccessibilityManager
Ensures screen reader compatibility and provides audio feedback.

**Interface:**
```typescript
interface AccessibilityManager {
  announce(message: string, priority?: 'low' | 'high'): void
  provideHapticFeedback(type: HapticType): void
  isScreenReaderEnabled(): boolean
}

type HapticType = 'success' | 'warning' | 'error' | 'selection'
```

**Responsibilities:**
- Announce messages via VoiceOver/TalkBack
- Trigger haptic feedback
- Detect screen reader status
- Format messages for accessibility

### Pi Server Components

#### CaptureService
Handles camera capture and image preprocessing.

**Interface:**
```python
class CaptureService:
    def capture_image(self) -> np.ndarray
    def preprocess_image(self, image: np.ndarray) -> np.ndarray
```

**Responsibilities:**
- Control Logitech C270 camera
- Activate LED ring lighting
- Apply OpenCV preprocessing (deskew, contrast adjustment)
- Return preprocessed image for OCR

#### OCRService
Extracts text from preprocessed images.

**Interface:**
```python
class OCRService:
    def extract_text(self, image: np.ndarray, engine: str) -> OCRResult

class OCRResult:
    text: str
    confidence: float
    detected_language: str
    paragraph_count: int
```

**Responsibilities:**
- Run Tesseract OCR (offline mode)
- Run Google Vision API (cloud mode)
- Detect document language
- Count paragraphs
- Return structured OCR results

#### TTSService
Synthesizes speech from text.

**Interface:**
```python
class TTSService:
    def synthesize(
        self,
        text: str,
        language: str,
        rate: float,
        pitch: str
    ) -> bytes
```

**Responsibilities:**
- Generate TTS audio using Coqui or Google TTS
- Support Arabic, French, English, Darija
- Apply speech rate and pitch settings
- Return audio data as bytes

#### TranslationService
Translates text between supported languages.

**Interface:**
```python
class TranslationService:
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str
```

**Responsibilities:**
- Translate text using translation API
- Support Arabic, French, English, Darija
- Handle translation errors
- Return translated text

#### HistoryService
Manages document history persistence.

**Interface:**
```python
class HistoryService:
    def save_scan(
        self,
        text: str,
        audio_path: str,
        language: str
    ) -> str
    def get_all(self) -> List[HistoryEntry]
    def get_by_id(self, entry_id: str) -> HistoryEntry
    def delete(self, entry_id: str) -> None
```

**Responsibilities:**
- Save scan results to disk
- Generate auto-titles (first 6 words)
- Store audio files
- Retrieve history entries
- Delete entries and associated files

#### SettingsService
Manages configuration persistence.

**Interface:**
```python
class SettingsService:
    def load_settings(self) -> Dict[str, Any]
    def save_settings(self, settings: Dict[str, Any]) -> None
```

**Responsibilities:**
- Load settings from disk
- Persist settings changes
- Validate setting values
- Provide default values

#### WebSocketAudioStreamer
Streams TTS audio to mobile clients.

**Interface:**
```python
class WebSocketAudioStreamer:
    def stream_audio(self, audio_data: bytes, client_id: str) -> None
    def stop_stream(self, client_id: str) -> None
```

**Responsibilities:**
- Maintain WebSocket connections
- Stream audio chunks to clients
- Handle client disconnections
- Manage multiple concurrent streams

### REST API Endpoints

**POST /api/capture**
- Triggers document scan
- Returns: `{ id, text, audioUrl, timestamp, language, paragraphCount }`

**GET /api/history**
- Retrieves all history entries
- Returns: `[{ id, title, timestamp }]`

**GET /api/history/<id>**
- Retrieves specific history entry
- Returns: `{ id, title, text, audioUrl, timestamp, language }`

**DELETE /api/history/<id>**
- Deletes history entry and audio file
- Returns: `{ success: true }`

**GET /api/settings**
- Retrieves current settings
- Returns: `Settings` object

**POST /api/settings**
- Updates settings
- Body: Partial `Settings` object
- Returns: Updated `Settings` object

**POST /api/stop**
- Stops current TTS playback
- Returns: `{ success: true }`

**POST /api/translate**
- Translates text
- Body: `{ text, sourceLanguage, targetLanguage }`
- Returns: `{ translatedText, audioUrl }`

**GET /api/health**
- Health check endpoint
- Returns: `{ status: 'ok', timestamp }`

## Data Models

### ScanResult
```typescript
interface ScanResult {
  id: string              // UUID
  text: string            // Extracted text
  audioUrl: string        // URL to TTS audio file
  timestamp: Date         // Scan timestamp
  language: Language      // Detected/configured language
  paragraphCount: number  // Number of paragraphs
}
```

### HistoryEntry
```typescript
interface HistoryEntry {
  id: string              // UUID
  title: string           // Auto-generated (first 6 words)
  text: string            // Full extracted text
  audioUrl: string        // URL to TTS audio file
  timestamp: Date         // Scan timestamp
  language: Language      // Document language
  translated?: {
    targetLanguage: Language
    text: string
    audioUrl: string
  }
}
```

### Settings
```typescript
interface Settings {
  language: Language                              // Default: 'french'
  speechRate: number                              // 0.5 - 2.0, default: 1.0
  speechPitch: 'low' | 'normal' | 'high'         // Default: 'normal'
  readingMode: 'continuous' | 'paragraph' | 'section'  // Default: 'continuous'
  audioOutput: 'pi-speaker' | 'phone' | 'bluetooth'    // Default: 'pi-speaker'
  ocrEngine: 'tesseract' | 'cloud'               // Default: 'tesseract'
}
```

### VoiceCommand
```typescript
type VoiceCommand = 
  | { type: 'scan' }
  | { type: 'repeat' }
  | { type: 'stop' }
  | { type: 'speed', direction: 'faster' | 'slower' }
  | { type: 'translate', language: Language }
  | { type: 'history' }
  | { type: 'share' }
  | { type: 'search', keyword: string }
  | { type: 'delete' }
```

### ConnectionStatus
```typescript
type ConnectionStatus = 'connected' | 'disconnected' | 'connecting'
```

### AudioOutput
```typescript
type AudioOutput = 'pi-speaker' | 'phone' | 'bluetooth'
```

### Language
```typescript
type Language = 'arabic' | 'french' | 'english' | 'darija'
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Connection state changes produce feedback
*For any* connection state change (connected, disconnected, reconnected), the Mobile_App should provide both haptic feedback and an appropriate audio announcement via the Screen_Reader.
**Validates: Requirements 1.2, 1.4, 1.5**

### Property 2: Health check polling interval
*For any* time period while the Mobile_App is running and connected, health check pings to the Pi_Server should occur at 5-second intervals (±500ms tolerance).
**Validates: Requirements 1.3**

### Property 3: Scan triggers API call
*For any* scan trigger (voice command "Read document" or scan button activation), the Mobile_App should send a POST request to /api/capture on the Pi_Server.
**Validates: Requirements 2.1, 4.2**

### Property 4: Image preprocessing is applied
*For any* captured image, the Pi_Server should apply OpenCV preprocessing (deskew and contrast adjustment) before OCR.
**Validates: Requirements 2.3**

### Property 5: OCR engine selection
*For any* preprocessed image, the Pi_Server should run OCR using the configured OCR_Engine (Tesseract or Google Vision API).
**Validates: Requirements 2.4**

### Property 6: Successful scan persistence
*For any* successful OCR extraction, the Pi_Server should generate TTS audio and save the scan (text, audio, metadata) to Reading_History.
**Validates: Requirements 2.6, 5.1**

### Property 7: Scan completion announcement
*For any* successful scan, the Mobile_App should announce "Scan complete. Found N paragraphs of text. Now playing" where N matches the actual paragraph count.
**Validates: Requirements 2.7**

### Property 8: TTS uses configured settings
*For any* OCR extraction result, the Pi_Server should generate TTS audio using the configured language, speech rate, and speech pitch settings.
**Validates: Requirements 3.1**

### Property 9: Audio streaming via WebSocket
*For any* generated TTS audio, the Pi_Server should stream audio chunks to the Mobile_App via WebSocket at /ws/audio.
**Validates: Requirements 3.2**

### Property 10: Audio output routing
*For any* received audio chunks, the Mobile_App should play audio through the configured output device (Pi speaker, phone speaker, or Bluetooth).
**Validates: Requirements 3.3**

### Property 11: Stop command halts playback
*For any* stop trigger (voice command "Stop" or stop button activation), the Mobile_App should send POST /api/stop and halt playback immediately.
**Validates: Requirements 3.4, 4.7**

### Property 12: Repeat command replays last scan
*For any* repeat trigger (voice command "Repeat last" or repeat button activation), the Mobile_App should replay the most recent scan from Reading_History.
**Validates: Requirements 3.6, 4.3**

### Property 13: Voice command speed adjustment
*For any* voice command "Slower" or "Faster", the Mobile_App should adjust the speech rate setting by ±0.1 via /api/settings and stay within the valid range [0.5, 2.0].
**Validates: Requirements 4.4, 4.5**

### Property 14: Voice command language switching
*For any* voice command "Translate to [language]" where language is Arabic, French, English, or Darija, the Mobile_App should update the TTS language setting via /api/settings.
**Validates: Requirements 4.6**

### Property 15: Voice command navigation
*For any* voice command "Show history", the Mobile_App should navigate to the History screen.
**Validates: Requirements 4.8**

### Property 16: Voice command share
*For any* voice command "Share", the Mobile_App should open the share sheet with the last recognized text.
**Validates: Requirements 4.9**

### Property 17: Voice command search
*For any* voice command "Search [keyword]", the Mobile_App should filter Reading_History to entries containing the keyword and announce the result count.
**Validates: Requirements 4.10**

### Property 18: Voice command delete
*For any* voice command "Delete last", the Mobile_App should delete the most recent history entry via DELETE /api/history/<id>.
**Validates: Requirements 4.11**

### Property 19: History retrieval on navigation
*For any* navigation to the History screen, the Mobile_App should retrieve all past scans via GET /api/history.
**Validates: Requirements 5.2**

### Property 20: History load announcement
*For any* successful history load, the Mobile_App should announce "History loaded. N documents found. Say the number of any document to replay it" where N matches the actual entry count.
**Validates: Requirements 5.3**

### Property 21: History title generation
*For any* history entry, the auto-generated title should be the first 6 words of the recognized text (or fewer if text has less than 6 words).
**Validates: Requirements 5.4**

### Property 22: History entry selection
*For any* selected history entry, the Mobile_App should retrieve full text and audio via GET /api/history/<id>.
**Validates: Requirements 5.5**

### Property 23: History entry deletion
*For any* delete action (swipe or voice command), the Mobile_App should send DELETE /api/history/<id> and remove the entry from local state.
**Validates: Requirements 5.6**

### Property 24: History search filtering
*For any* search keyword, the Mobile_App should return only history entries where the text contains the keyword (case-insensitive).
**Validates: Requirements 5.7**

### Property 25: Cache size limit
*For any* state of the Mobile_App cache, the number of cached scans should never exceed 20 entries (oldest entries removed first).
**Validates: Requirements 5.8, 8.1**

### Property 26: Settings retrieval on navigation
*For any* navigation to the Settings screen, the Mobile_App should retrieve current settings via GET /api/settings.
**Validates: Requirements 6.1**

### Property 27: Settings persistence
*For any* setting change, the Mobile_App should immediately send POST /api/settings to persist the change.
**Validates: Requirements 6.2**

### Property 28: Settings change feedback
*For any* setting change, the Mobile_App should provide haptic feedback and announce the change (e.g., "Language changed to Arabic").
**Validates: Requirements 6.3**

### Property 29: Speech rate validation
*For any* speech rate setting value, the Mobile_App should accept values in the range [0.5, 2.0] and reject values outside this range.
**Validates: Requirements 6.5**

### Property 30: Share action opens share sheet
*For any* share trigger (voice command or button), the Mobile_App should open the native share sheet with the recognized text.
**Validates: Requirements 7.2**

### Property 31: Clipboard copy
*For any* clipboard copy action, the text should be correctly copied to the system clipboard and retrievable.
**Validates: Requirements 7.6**

### Property 32: Share action announcement
*For any* completed share action, the Mobile_App should announce the action (e.g., "Text copied to clipboard" or "Opening WhatsApp").
**Validates: Requirements 7.7**

### Property 33: Offline cached history access
*For any* state where the Pi_Server is unreachable, the Mobile_App should display and provide audio playback for cached history entries.
**Validates: Requirements 8.2**

### Property 34: Offline announcement
*For any* transition to offline state, the Mobile_App should announce "Smart Reader is not connected. Showing cached history".
**Validates: Requirements 8.3**

### Property 35: Offline settings queueing
*For any* setting change while offline, the Mobile_App should queue the change locally without sending to the Pi_Server.
**Validates: Requirements 8.5**

### Property 36: Settings sync on reconnection
*For any* reconnection after offline period, the Mobile_App should automatically sync all queued settings changes to the Pi_Server.
**Validates: Requirements 8.6**

### Property 37: Interactive elements have accessibility labels
*For any* interactive UI element, the element should have an appropriate accessibility label and hint for Screen_Reader announcement.
**Validates: Requirements 9.2, 9.8**

### Property 38: State changes produce feedback
*For any* state change (connection, scan, playback, settings), the Mobile_App should provide both haptic feedback and audio announcement.
**Validates: Requirements 9.3**

### Property 39: Announcements use active voice
*For any* announcement text, the text should use active, imperative language and not contain passive voice patterns (e.g., "is being", "will be").
**Validates: Requirements 9.4**

### Property 40: Announcements avoid visual metaphors
*For any* announcement text, the text should not contain visual metaphors (colors, positions, visual elements like "blue button", "top of screen").
**Validates: Requirements 9.5**

### Property 41: Text display includes audio
*For any* text displayed on screen, the Mobile_App should also provide audio confirmation via Screen_Reader.
**Validates: Requirements 9.6**

### Property 42: Announcement length limit
*For any* announcement, the text should contain at most 3 sentences (determined by period count ≤ 3).
**Validates: Requirements 9.7**

### Property 43: Failed request queueing
*For any* failed API request when Pi_Server is unreachable, the Mobile_App should queue the request and retry automatically on reconnection.
**Validates: Requirements 10.5**

### Property 44: Error feedback
*For any* error condition, the Mobile_App should provide haptic feedback and a concise, actionable error message.
**Validates: Requirements 10.6**

### Property 45: Error messages avoid apologetic language
*For any* error message, the text should not contain apologetic or hedging phrases (e.g., "sorry", "unfortunately", "we apologize").
**Validates: Requirements 10.7**

### Property 46: Language detection attempted
*For any* OCR extraction result, the Pi_Server should attempt to auto-detect the document language.
**Validates: Requirements 11.1**

### Property 47: Language mismatch announcement
*For any* detected document language that differs from configured TTS language, the Mobile_App should announce "Document appears to be in [detected language]. Current TTS language is [configured language]".
**Validates: Requirements 11.2**

### Property 48: Language mismatch offers switch
*For any* language mismatch detection, the Mobile_App should offer to switch TTS language to match the document.
**Validates: Requirements 11.3**

### Property 49: Language switch confirmation
*For any* confirmed language switch, the Mobile_App should update settings via /api/settings and announce "Language changed to [new language]".
**Validates: Requirements 11.4**

### Property 50: Translation request sent
*For any* translation voice command "Translate to [language]", the Mobile_App should send the recognized text to the translation service.
**Validates: Requirements 12.2**

### Property 51: Translation completion announcement
*For any* successful translation, the Mobile_App should announce "Translation complete" and play the translated text using the target language TTS_Engine.
**Validates: Requirements 12.3**

### Property 52: Translation preserves original
*For any* translation request, the original text and audio should remain in Reading_History unchanged.
**Validates: Requirements 12.4**

### Property 53: Translation storage
*For any* saved translated document, both original and translated versions should be stored with clear labels indicating source and target languages.
**Validates: Requirements 12.5**

### Property 54: Translated document announcement
*For any* translated document displayed in history, the Mobile_App should announce "Original language: [source], Translated to: [target]".
**Validates: Requirements 12.7**

### Property 55: Scan result display
*For any* completed scan, the Home screen should display the recognized text.
**Validates: Requirements 13.5**

### Property 56: Button activation feedback
*For any* button activation (scan, stop, repeat), the Mobile_App should provide haptic feedback.
**Validates: Requirements 13.6**


## Error Handling

### Connection Errors

**Pi Server Unreachable**
- Detection: Health check ping fails or API request times out
- Response: Announce "Smart Reader is not connected. Please check your Wi-Fi or move closer to the device"
- Recovery: Queue failed requests, offer cached history, auto-retry on reconnection
- User Action: Check Wi-Fi, move closer to device, or use cached history

**WebSocket Disconnection**
- Detection: WebSocket connection drops during audio streaming
- Response: Automatically retry connection once
- Recovery: If retry fails, announce "Audio connection lost. Please try again"
- User Action: Trigger scan again or replay from history

### OCR Errors

**No Text Detected**
- Detection: OCR returns empty string or whitespace only
- Response: Announce "No text was detected. Please try repositioning the document and scanning again"
- Recovery: None (user must rescan)
- User Action: Reposition document, ensure good lighting, rescan

**OCR Engine Failure**
- Detection: OCR process crashes or times out
- Response: Announce "Scan failed. Please try again"
- Recovery: Log error, return to ready state
- User Action: Retry scan

### TTS Errors

**TTS Synthesis Failure**
- Detection: TTS engine returns error or empty audio
- Response: Announce "Text-to-speech unavailable. Text will be displayed only"
- Recovery: Display text on screen, enable screen reader access
- User Action: Enable screen reader or check TTS settings

**Audio Playback Failure**
- Detection: Audio player fails to initialize or play
- Response: Announce "Audio playback failed. Please check your audio settings"
- Recovery: Display text on screen
- User Action: Check audio output settings, restart app

### Translation Errors

**Translation Service Unavailable**
- Detection: Translation API returns error or times out
- Response: Announce "Translation unavailable. Please check your internet connection"
- Recovery: Keep original text available
- User Action: Check internet connection, retry translation

**Unsupported Language Pair**
- Detection: Translation service doesn't support requested language pair
- Response: Announce "Translation not available for this language combination"
- Recovery: Keep original text available
- User Action: Use different language or skip translation

### Settings Errors

**Invalid Setting Value**
- Detection: Setting value outside valid range or invalid type
- Response: Announce "Invalid setting value. Using previous value"
- Recovery: Revert to previous valid value
- User Action: Choose valid setting value

**Settings Persistence Failure**
- Detection: POST /api/settings returns error
- Response: Announce "Settings could not be saved. Changes will be temporary"
- Recovery: Queue change for retry, apply locally
- User Action: Check connection, retry later

### History Errors

**History Retrieval Failure**
- Detection: GET /api/history returns error or times out
- Response: Announce "Could not load history. Showing cached entries"
- Recovery: Display cached history
- User Action: Check connection, retry later

**History Deletion Failure**
- Detection: DELETE /api/history/<id> returns error
- Response: Announce "Could not delete entry. Please try again"
- Recovery: Keep entry in local state
- User Action: Check connection, retry deletion

### Voice Command Errors

**Recognition Failure**
- Detection: Voice recognition returns error or no result
- Response: Announce "Voice command not recognized. Please try again"
- Recovery: Continue listening for next command
- User Action: Speak command more clearly

**Ambiguous Command**
- Detection: Voice recognition returns multiple possible interpretations
- Response: Announce "Command unclear. Please repeat"
- Recovery: Continue listening for next command
- User Action: Speak command more clearly

### General Error Handling Principles

1. **Always provide haptic feedback** for errors
2. **Use concise, actionable error messages** (1-2 sentences)
3. **Never over-apologize** or use hedging language
4. **Offer specific recovery actions** when possible
5. **Maintain app state** - never crash or freeze
6. **Log errors** for debugging without exposing technical details to users
7. **Auto-retry** transient failures (network, connection)
8. **Degrade gracefully** - provide reduced functionality rather than failing completely

## Testing Strategy

### Overview

The SmartReader testing strategy employs a dual approach combining unit tests for specific examples and edge cases with property-based tests for universal correctness properties. This comprehensive strategy ensures both concrete functionality and general correctness across all inputs.

### Property-Based Testing

**Framework**: fast-check (JavaScript/TypeScript)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `Feature: smartreader-mobile-app, Property N: [property text]`

**Property Test Categories**:

1. **Connection Properties** (Properties 1-2)
   - Test connection state transitions with random timing
   - Verify health check intervals with time-based generators
   - Generate random connection/disconnection sequences

2. **Scan and OCR Properties** (Properties 3-7)
   - Generate random scan triggers (voice, button)
   - Test with various image preprocessing scenarios
   - Verify OCR engine selection with random settings
   - Test scan persistence with random text content

3. **Audio and Playback Properties** (Properties 8-12)
   - Generate random TTS settings combinations
   - Test audio streaming with random chunk sizes
   - Verify playback control with random timing
   - Test output routing with random device selections

4. **Voice Command Properties** (Properties 13-18)
   - Generate random voice commands
   - Test speed adjustments with random increments
   - Verify language switching with all language combinations
   - Test navigation and actions with random sequences

5. **History Properties** (Properties 19-25)
   - Generate random history entries
   - Test title generation with various text lengths
   - Verify search with random keywords
   - Test cache limits with random entry counts

6. **Settings Properties** (Properties 26-29)
   - Generate random setting values
   - Test validation with boundary values
   - Verify persistence with random setting combinations
   - Test feedback with all setting types

7. **Sharing Properties** (Properties 30-32)
   - Generate random text content for sharing
   - Test clipboard operations with various text formats
   - Verify announcements with random share targets

8. **Offline Properties** (Properties 33-36)
   - Generate random offline/online transitions
   - Test queueing with random operation sequences
   - Verify sync with random queued changes

9. **Accessibility Properties** (Properties 37-42)
   - Generate random UI elements and verify labels
   - Test announcements with random state changes
   - Verify language patterns with text analysis
   - Test length limits with random announcement text

10. **Error Handling Properties** (Properties 43-45)
    - Generate random error conditions
    - Test queueing with random failure sequences
    - Verify error messages with pattern matching

11. **Language Properties** (Properties 46-49)
    - Generate random language combinations
    - Test detection with various text samples
    - Verify mismatch handling with all language pairs

12. **Translation Properties** (Properties 50-54)
    - Generate random translation requests
    - Test preservation with random text content
    - Verify storage with random language pairs

13. **UI Properties** (Properties 55-56)
    - Generate random scan results
    - Test feedback with random button activations

### Unit Testing

**Framework**: Jest (JavaScript/TypeScript), pytest (Python)

**Unit Test Categories**:

1. **Component Tests** (Mobile App)
   - ConnectionManager: connection establishment, status updates
   - VoiceCommandEngine: command parsing, recognition
   - ScanController: scan workflow, error handling
   - AudioPlayer: playback control, output routing
   - HistoryManager: CRUD operations, caching
   - SettingsManager: validation, persistence
   - ShareManager: share sheet, clipboard
   - AccessibilityManager: announcements, haptic feedback

2. **Service Tests** (Pi Server)
   - CaptureService: camera control, preprocessing
   - OCRService: text extraction, language detection
   - TTSService: audio synthesis, language support
   - TranslationService: translation API integration
   - HistoryService: file operations, metadata
   - SettingsService: configuration management
   - WebSocketAudioStreamer: streaming, connection management

3. **API Tests** (Pi Server)
   - POST /api/capture: successful scan, OCR failure, camera error
   - GET /api/history: empty history, multiple entries
   - GET /api/history/<id>: valid ID, invalid ID
   - DELETE /api/history/<id>: successful delete, not found
   - GET /api/settings: default settings, custom settings
   - POST /api/settings: valid updates, invalid values
   - POST /api/stop: playback active, no playback
   - POST /api/translate: successful translation, API failure
   - GET /api/health: server healthy

4. **Integration Tests**
   - End-to-end scan workflow: trigger → capture → OCR → TTS → playback
   - History workflow: scan → save → retrieve → replay → delete
   - Settings workflow: change → persist → retrieve → apply
   - Translation workflow: scan → translate → save → replay
   - Offline workflow: disconnect → queue → reconnect → sync
   - Voice command workflow: recognize → parse → execute → feedback

5. **Edge Case Tests**
   - Empty OCR results
   - WebSocket disconnection during playback
   - TTS synthesis failure
   - Translation service unavailable
   - Offline scan attempt
   - Invalid setting values
   - Cache overflow (>20 entries)
   - Rapid connection state changes
   - Concurrent voice commands
   - Very long text content
   - Special characters in text
   - Multiple language switches

### Test Data Generators

**For Property-Based Tests**:

```typescript
// Connection status generator
const connectionStatusArb = fc.constantFrom('connected', 'disconnected', 'connecting')

// Language generator
const languageArb = fc.constantFrom('arabic', 'french', 'english', 'darija')

// Speech rate generator (0.5 - 2.0)
const speechRateArb = fc.double({ min: 0.5, max: 2.0 })

// Text content generator
const textContentArb = fc.string({ minLength: 1, maxLength: 1000 })

// History entry generator
const historyEntryArb = fc.record({
  id: fc.uuid(),
  title: fc.string({ minLength: 1, maxLength: 50 }),
  text: textContentArb,
  audioUrl: fc.webUrl(),
  timestamp: fc.date(),
  language: languageArb
})

// Voice command generator
const voiceCommandArb = fc.oneof(
  fc.constant({ type: 'scan' }),
  fc.constant({ type: 'repeat' }),
  fc.constant({ type: 'stop' }),
  fc.record({ type: fc.constant('speed'), direction: fc.constantFrom('faster', 'slower') }),
  fc.record({ type: fc.constant('translate'), language: languageArb }),
  fc.constant({ type: 'history' }),
  fc.constant({ type: 'share' }),
  fc.record({ type: fc.constant('search'), keyword: fc.string({ minLength: 1 }) }),
  fc.constant({ type: 'delete' })
)

// Settings generator
const settingsArb = fc.record({
  language: languageArb,
  speechRate: speechRateArb,
  speechPitch: fc.constantFrom('low', 'normal', 'high'),
  readingMode: fc.constantFrom('continuous', 'paragraph', 'section'),
  audioOutput: fc.constantFrom('pi-speaker', 'phone', 'bluetooth'),
  ocrEngine: fc.constantFrom('tesseract', 'cloud')
})
```

### Test Execution

**Continuous Integration**:
- Run all unit tests on every commit
- Run property tests on every pull request
- Run integration tests nightly
- Fail build on any test failure

**Local Development**:
- Run relevant unit tests before committing
- Run property tests for modified components
- Run integration tests before pull request

**Test Coverage Goals**:
- Unit test coverage: >80% for all components
- Property test coverage: 100% of correctness properties
- Integration test coverage: All critical user workflows
- Edge case coverage: All identified error conditions

### Mocking Strategy

**Mobile App Tests**:
- Mock Pi Server API responses using json-server or MSW
- Mock WebSocket connections for audio streaming tests
- Mock voice recognition for command tests
- Mock native modules (haptics, screen reader, share)

**Pi Server Tests**:
- Mock camera hardware for capture tests
- Mock OCR engines (Tesseract, Google Vision)
- Mock TTS engines (Coqui, Google TTS)
- Mock translation API
- Mock file system for history tests

**Integration Tests**:
- Use real Pi Server with test database
- Use real WebSocket connections
- Mock only external services (Google Vision, Google TTS, translation API)

### Performance Testing

**Response Time Targets**:
- API endpoints: <200ms (95th percentile)
- OCR processing: <3 seconds for standard document
- TTS generation: <2 seconds for 1000 characters
- WebSocket audio latency: <100ms
- Voice command recognition: <500ms

**Load Testing**:
- Concurrent scans: Support 1 user (single-user device)
- History size: Test with 100+ entries
- Cache performance: Test with 20 cached entries
- WebSocket stability: Test 30-minute continuous streaming

### Accessibility Testing

**Automated Tests**:
- Verify all interactive elements have accessibility labels
- Check announcement text patterns (active voice, no visual metaphors)
- Validate announcement length limits
- Test haptic feedback triggers

**Manual Testing**:
- Test with VoiceOver on iOS
- Test with TalkBack on Android
- Verify all workflows are completable without sight
- Test with real visually impaired users

### Test Documentation

Each test should include:
- Clear description of what is being tested
- Reference to requirements and design properties
- Expected behavior
- Test data and scenarios
- Pass/fail criteria

Example:
```typescript
/**
 * Property 13: Voice command speed adjustment
 * 
 * Validates: Requirements 4.4, 4.5
 * 
 * For any voice command "Slower" or "Faster", the Mobile_App should adjust
 * the speech rate setting by ±0.1 via /api/settings and stay within the
 * valid range [0.5, 2.0].
 */
test('Feature: smartreader-mobile-app, Property 13: Voice command speed adjustment', () => {
  fc.assert(
    fc.property(
      fc.double({ min: 0.5, max: 2.0 }),
      fc.constantFrom('faster', 'slower'),
      (initialRate, direction) => {
        // Test implementation
      }
    ),
    { numRuns: 100 }
  )
})
```
