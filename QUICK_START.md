# SmartReader - Quick Start Guide

## Prerequisites

### For Pi Server
- Python 3.8 or higher
- pip (Python package manager)

### For Mobile App
- Node.js 18 or higher
- npm or yarn
- Expo Go app on your phone (for testing)

## Step 1: Start the Pi Server

```bash
# Navigate to pi-server directory
cd pi-server

# Install dependencies (first time only)
pip install -r requirements.txt

# Install system dependencies (Raspberry Pi only)
# sudo apt-get install tesseract-ocr tesseract-ocr-ara tesseract-ocr-fra tesseract-ocr-eng ffmpeg

# Start the server
python -m src.app
```

The server will start on `http://localhost:5000`

You should see:
```
 * Running on http://0.0.0.0:5000
 * Running on http://192.168.x.x:5000
```

## Step 2: Start the Mobile App

```bash
# Navigate to mobile app directory
cd smartreader-mobile-clean

# Install dependencies (first time only)
npm install

# Start Expo development server
npm start
```

You should see a QR code in the terminal.

## Step 3: Run on Your Device

### Option A: Physical Device (Recommended)

1. Install **Expo Go** app from:
   - iOS: App Store
   - Android: Google Play Store

2. Scan the QR code from the terminal:
   - iOS: Use Camera app
   - Android: Use Expo Go app

3. The app will load on your device

### Option B: Emulator/Simulator

```bash
# For Android emulator
npm run android

# For iOS simulator (Mac only)
npm run ios

# For web browser
npm run web
```

## Step 4: Configure Connection

### If Pi Server is on the same machine:

The app should auto-connect to `http://smartreader.local:5000`

### If Pi Server is on a different machine:

1. Find the Pi Server IP address:
   ```bash
   # On Pi Server terminal, look for the IP in the startup message
   # Example: http://192.168.1.100:5000
   ```

2. Update the mobile app:
   - Open `smartreader-mobile-clean/src/services/api.ts`
   - Change line 11:
     ```typescript
     constructor(hostname: string = '192.168.1.100', port: number = 5000) {
     ```
   - Replace `192.168.1.100` with your Pi Server IP

3. Restart the mobile app

## Step 5: Test the System

### Test Connection

1. Open the mobile app
2. Check the status badge at the top
3. Should show "Connected" in green
4. If "Disconnected", tap "Reconnect"

### Test Scanning

1. Tap the large blue "SCAN" button
2. Wait for the scan to complete (~3-5 seconds)
3. You should see:
   - Recognized text below the button
   - Language and paragraph count
   - Entry saved to history

**Note**: Without a camera, the scan will fail. For testing without hardware, you can modify the capture service to use a test image.

### Test History

1. Navigate to "History" tab (bottom navigation)
2. You should see your scan in the list
3. Tap an entry to view details
4. Long press to delete

### Test Settings

1. Navigate to "Settings" tab (bottom navigation)
2. Try changing:
   - Language (Arabic, French, English, Darija)
   - Speech Rate (use +/- buttons)
   - Speech Pitch (Low, Normal, High)
   - OCR Engine (Tesseract or Cloud)
3. Changes save automatically

## Troubleshooting

### Mobile App Won't Connect

**Problem**: Status shows "Disconnected"

**Solutions**:
1. Check Pi Server is running
2. Check both devices are on same Wi-Fi network
3. Update hostname/IP in `src/services/api.ts`
4. Check firewall isn't blocking port 5000
5. Try using IP address instead of `smartreader.local`

### Scan Fails

**Problem**: "Failed to capture image from camera"

**Solutions**:
1. Check camera is connected (Raspberry Pi only)
2. For testing without camera, modify `capture_service.py`:
   ```python
   def capture_image(self):
       # For testing: return a test image
       import cv2
       return cv2.imread('test_image.jpg')
   ```

### OCR Returns No Text

**Problem**: "No text detected in image"

**Solutions**:
1. Check Tesseract is installed: `tesseract --version`
2. Install language packs:
   ```bash
   sudo apt-get install tesseract-ocr-ara tesseract-ocr-fra tesseract-ocr-eng
   ```
3. Try using Cloud OCR engine in settings

### TTS Fails

**Problem**: Audio URL is null

**Solutions**:
1. Check Coqui TTS is installed: `pip install TTS`
2. For Google TTS, set credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```
3. Check `audio/` directory exists and is writable

### TypeScript Errors

**Problem**: Red squiggly lines in VS Code

**Solutions**:
1. Run: `npm install` in `smartreader-mobile-clean/`
2. Restart VS Code
3. Check: `npx tsc --noEmit` for errors

## Development Tips

### Hot Reload

Both server and mobile app support hot reload:
- **Pi Server**: Automatically reloads on file changes
- **Mobile App**: Shake device or press `r` in terminal to reload

### Debugging

**Pi Server**:
```bash
# Check logs in terminal
# Add print statements or use logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Mobile App**:
```bash
# Open React Native debugger
# Shake device → "Debug" → Opens Chrome DevTools
# Or use console.log() statements
```

### Testing API Endpoints

Use curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Get settings
curl http://localhost:5000/api/settings

# Update settings
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"language": "arabic"}'

# Get history
curl http://localhost:5000/api/history
```

## Next Steps

1. **Add Test Data**: Create some test scans to populate history
2. **Customize Settings**: Adjust language, speech rate, etc.
3. **Test Offline Mode**: Disconnect Pi Server and check cached history
4. **Explore Code**: Check implementation files for details
5. **Add Features**: Implement voice commands, audio playback, etc.

## Getting Help

- Check `IMPLEMENTATION_SUMMARY.md` for full system overview
- Check `MOBILE_APP_COMPLETE.md` for mobile app details
- Check `pi-server/TASKS_3_4_5_COMPLETE.md` for backend details
- Review code comments for implementation details

## Common Commands

### Pi Server
```bash
cd pi-server
python -m src.app                    # Start server
pip install -r requirements.txt      # Install dependencies
python -m pytest                     # Run tests (when added)
```

### Mobile App
```bash
cd smartreader-mobile-clean
npm start                            # Start dev server
npm run android                      # Run on Android
npm run ios                          # Run on iOS
npm run web                          # Run on web
npx tsc --noEmit                     # Check TypeScript
npm run lint                         # Run linter
```

## Success Indicators

You'll know everything is working when:

✅ Pi Server starts without errors
✅ Mobile app shows "Connected" status
✅ Scan button works (even if camera fails)
✅ History shows scans
✅ Settings can be changed
✅ No TypeScript errors
✅ No console errors in mobile app

Happy coding! 🚀
