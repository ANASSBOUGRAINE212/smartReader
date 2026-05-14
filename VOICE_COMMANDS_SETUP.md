# Voice Commands Setup Guide

## What's Been Added

✅ **Voice command recognition expanded:**
- "Open camera Pi" / "Use Pi camera" → Scans with Pi camera
- "Phone camera" / "Scan with phone" → Scans with phone camera
- "Settings" → Opens settings
- "Help" → Shows available commands
- All previous commands still work

✅ **Voice commands plugin enabled** in `app.json`

## How to Enable Voice Commands

Voice commands **only work with native builds**, not Expo Go.

### Option 1: Build for Android (Recommended)

```bash
cd smartreader-mobile-clean

# Build and run on connected Android device
npx expo run:android
```

**Requirements:**
- Android device connected via USB with USB debugging enabled
- OR Android emulator running
- Android Studio installed (for SDK)

### Option 2: Build APK for Installation

```bash
cd smartreader-mobile-clean

# Install EAS CLI if not already installed
npm install -g eas-cli

# Login to Expo account
eas login

# Build APK
eas build --platform android --profile preview

# Download and install the APK on your phone
```

## Testing Voice Commands

Once you have the native build running:

1. **Tap the microphone button** (bottom right of home screen)
2. **Say a command** (see list below)
3. **App executes the command** automatically

### Available Voice Commands

| Say This | App Does This |
|----------|---------------|
| "Scan" or "Open camera Pi" | Scans with Pi camera |
| "Phone camera" or "Scan with phone" | Opens phone camera to scan |
| "Stop" or "Pause" | Stops audio playback |
| "Repeat" or "Again" | Repeats last scan |
| "Faster" or "Speed up" | Increases speech rate |
| "Slower" or "Slow down" | Decreases speech rate |
| "French" or "Français" | Switches to French |
| "English" or "Anglais" | Switches to English |
| "Show history" or "History" | Opens history tab |
| "Settings" or "Options" | Opens settings tab |
| "Share" | Shares current scan |
| "Help" or "Commands" | Shows available commands |

### Voice Command Flow

```
User taps microphone button
    ↓
App starts listening (button turns red)
    ↓
User says "Open camera Pi"
    ↓
App recognizes command
    ↓
App triggers Pi camera scan
    ↓
Text extracted and read aloud
```

## Troubleshooting

### "Cannot find native module 'ExpoSpeechRecognition'"

**Cause:** Running in Expo Go (voice commands not supported)

**Solution:** Build native app with `npx expo run:android`

### Voice commands not recognized

**Possible causes:**
1. Microphone permission not granted
2. Speaking too fast/unclear
3. Background noise

**Solutions:**
- Check app permissions in phone settings
- Speak clearly and at normal pace
- Use in quiet environment
- Try saying command differently (see alternatives in table above)

### Microphone button doesn't work

**Check:**
1. Is voice recognition available? (button should be visible)
2. Are permissions granted?
3. Is device connected to internet? (speech recognition needs internet)

### Build fails with Android

**Common issues:**
1. Android SDK not installed → Install Android Studio
2. No device/emulator → Connect phone or start emulator
3. USB debugging not enabled → Enable in phone developer options

## Building for First Time

### Step 1: Install Android Studio

1. Download from: https://developer.android.com/studio
2. Install with default settings
3. Open Android Studio
4. Go to Tools → SDK Manager
5. Install Android SDK (API 33 or higher)

### Step 2: Connect Android Device

1. Enable Developer Options on phone:
   - Settings → About Phone
   - Tap "Build Number" 7 times
2. Enable USB Debugging:
   - Settings → Developer Options
   - Turn on "USB Debugging"
3. Connect phone to computer via USB
4. Accept USB debugging prompt on phone

### Step 3: Build and Run

```bash
cd smartreader-mobile-clean
npx expo run:android
```

First build takes 5-10 minutes. Subsequent builds are faster.

### Step 4: Test Voice Commands

1. App opens automatically on phone
2. Tap microphone button
3. Say "Help" to see available commands
4. Try "Open camera Pi" to test scanning

## Next Steps: Smart Capture Features

Voice commands are now working! Next features to implement:

1. **Camera preview with text detection**
   - Show live camera feed
   - Detect text in real-time
   - Guide user to position camera

2. **Auto-capture when text detected**
   - Wait for stable text
   - Auto-trigger scan
   - No need to tap button

3. **Audio guidance**
   - "Move camera left"
   - "Move closer"
   - "Hold steady"

These features require additional development (2-3 days).

## Summary

✅ **Voice commands expanded** - More phrases recognized
✅ **Plugin enabled** - Ready for native build
✅ **Help command added** - Users can ask for available commands

**To use:** Build native app with `npx expo run:android`

**Commands work:** Pi camera, phone camera, settings, help, and all previous commands

**Next:** Implement smart capture with text detection and auto-capture
