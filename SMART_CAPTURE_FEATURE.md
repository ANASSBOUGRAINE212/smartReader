# Smart Capture Feature - Voice Commands + Auto Text Detection

## Current Status

✅ **Working:**
- Manual Pi camera scan
- Manual phone camera scan  
- Voice commands (disabled in Expo Go, works with `npx expo run:android`)
- Audio output selection (Pi speaker or phone)

## Requested Features

### 1. Voice-Activated Scanning

**User says:** "Open camera Pi" or "Scan with phone"

**App should:**
- Recognize voice command
- Automatically trigger camera scan
- No need to tap buttons

**Status:** ⚠️ Partially implemented
- Voice command parsing exists in `src/services/voice-commands.ts`
- Commands like "scan", "capture" already recognized
- **Issue:** Voice recognition only works with native build (`npx expo run:android`), not Expo Go
- **Solution:** Build native app or use Expo Go with manual buttons

### 2. Smart Pi Camera with Text Detection Guidance

**User says:** "Open camera Pi"

**App should:**
1. Show live camera preview from Pi
2. Detect if text is visible in frame
3. If no text detected:
   - Give audio feedback: "Move camera to the right/left/up/down"
   - Show visual indicator on screen
4. When text detected and stable:
   - Auto-capture image
   - Process with OCR
   - Read text aloud

**Current limitations:**
- Pi camera preview exists (`/api/camera/preview`) but not real-time
- No text detection in preview (would need OpenCV text detection)
- No guidance system

**What's needed:**
- Real-time video streaming from Pi (WebSocket or MJPEG)
- Text detection algorithm running on each frame
- Position calculation (where is text in frame)
- Audio guidance generation
- Auto-capture trigger when text is stable for 2-3 seconds

### 3. Smart Phone Camera with Auto-Capture

**User says:** "Scan with phone"

**App should:**
1. Open phone camera in preview mode
2. Detect text in real-time using phone's camera
3. Show visual feedback (green box around detected text)
4. When text is stable and clear:
   - Auto-capture photo
   - Apply smart image processing (deskew, enhance contrast)
   - Send to Pi for OCR
   - Read text aloud

**Current limitations:**
- Phone camera opens but immediately takes photo
- No real-time text detection
- No auto-capture logic

**What's needed:**
- Camera preview mode (not immediate capture)
- On-device text detection (ML Kit or similar)
- Image quality assessment
- Auto-capture trigger
- Smart image preprocessing before sending to Pi

## Implementation Plan

### Phase 1: Fix Audio Output (DONE ✅)

- [x] Audio only plays on selected output (Pi speaker OR phone)
- [x] Setting persists across scans

### Phase 2: Voice Commands (Requires Native Build)

**To enable voice commands:**

```bash
cd smartreader-mobile-clean
npx expo run:android
```

**Already implemented commands:**
- "Scan" / "Capture" / "Take picture" → Triggers Pi camera
- "Phone camera" → Triggers phone camera
- "Stop" → Stops playback
- "Repeat" → Repeats last scan
- "Faster" / "Slower" → Adjusts speech rate
- "French" / "English" → Changes language
- "Show history" → Opens history tab

**What to add:**
- "Open camera Pi" → Same as "Scan"
- "Scan with phone" → Same as "Phone camera"

### Phase 3: Smart Pi Camera (Complex)

**Step 1: Real-time Preview**
- Add WebSocket video streaming from Pi
- Display live preview in mobile app
- Overlay detection indicators

**Step 2: Text Detection**
- Add OpenCV text detection on Pi
- Run detection on each frame (or every N frames)
- Return detection results via WebSocket

**Step 3: Guidance System**
- Calculate text position in frame
- Generate guidance messages ("Move left", "Move closer")
- Send audio feedback to user
- Show visual arrows/indicators

**Step 4: Auto-Capture**
- Track text stability (same position for 2-3 seconds)
- Auto-trigger capture when stable
- Process with full OCR pipeline

**Estimated effort:** 2-3 days of development

### Phase 4: Smart Phone Camera (Complex)

**Step 1: Camera Preview Mode**
- Use `expo-camera` for live preview
- Don't capture immediately
- Show camera controls

**Step 2: On-Device Text Detection**
- Integrate ML Kit Text Recognition
- Run detection on camera frames
- Draw bounding boxes around detected text

**Step 3: Quality Assessment**
- Check image sharpness (blur detection)
- Check text size (too small/too far)
- Check lighting (too dark/bright)

**Step 4: Auto-Capture**
- Wait for stable, high-quality frame
- Auto-capture when conditions met
- Apply smart preprocessing
- Send to Pi for OCR

**Estimated effort:** 2-3 days of development

## Quick Wins (Can Do Now)

### 1. Enable Voice Commands

Build native app to enable voice commands:

```bash
cd smartreader-mobile-clean
npx expo run:android
```

Voice commands will work immediately!

### 2. Add More Voice Command Aliases

Update `src/services/voice-commands.ts` to recognize more phrases:

```typescript
// Add these patterns:
'open camera pi': 'scan',
'use pi camera': 'scan',
'scan with phone': 'phone_camera',
'use phone camera': 'phone_camera',
```

### 3. Add Visual Feedback

Show camera preview from Pi while scanning:
- Display `/api/camera/preview` image
- Refresh every 500ms
- Show "Scanning..." overlay

### 4. Add Audio Guidance (Simple Version)

After capture, if no text detected:
- Play audio: "No text detected. Please position camera over text and try again"
- Show helpful message on screen

## Recommended Approach

**For MVP (Minimum Viable Product):**

1. ✅ Fix audio output (DONE)
2. ✅ Enable voice commands with native build
3. Add simple camera preview during scan
4. Add "no text detected" feedback
5. Add manual "Recapture" button

**For Full Smart Capture:**

1. Implement real-time Pi camera streaming
2. Add text detection on Pi
3. Add guidance system
4. Add auto-capture logic
5. Implement phone camera preview mode
6. Add on-device text detection
7. Add auto-capture for phone

## Current Voice Commands

Already implemented (works with native build):

| Command | Action |
|---------|--------|
| "Scan", "Capture", "Take picture" | Scan with Pi camera |
| "Stop", "Pause" | Stop audio playback |
| "Repeat", "Again" | Repeat last scan |
| "Faster", "Speed up" | Increase speech rate |
| "Slower", "Slow down" | Decrease speech rate |
| "French" | Switch to French |
| "English" | Switch to English |
| "Show history", "History" | Open history tab |
| "Share" | Share current scan |

**To add:**
- "Open camera Pi" → Scan with Pi camera
- "Scan with phone" → Scan with phone camera
- "Help" → Show available commands

## Technical Requirements

### For Real-time Text Detection:

**Pi Server:**
- OpenCV with text detection (EAST detector or Tesseract)
- WebSocket for streaming frames
- Frame processing pipeline

**Mobile App:**
- WebSocket client for receiving frames
- Canvas for drawing detection overlays
- Audio feedback system

### For Phone Camera Smart Capture:

**Mobile App:**
- `expo-camera` for live preview
- ML Kit Text Recognition (or similar)
- Image quality assessment algorithms
- Auto-capture state machine

## Next Steps

1. **Immediate:** Transfer updated `api.py` to fix audio output
2. **Short-term:** Build native app to enable voice commands
3. **Medium-term:** Add simple camera preview and feedback
4. **Long-term:** Implement full smart capture features

Would you like me to:
- A) Fix audio output and enable voice commands (quick)
- B) Add simple camera preview and feedback (medium)
- C) Implement full smart capture with auto-detection (complex)

Choose A for immediate improvements, B for better UX, or C for the full vision!
