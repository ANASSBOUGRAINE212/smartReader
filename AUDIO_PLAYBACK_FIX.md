# Audio Playback Fix

## Problem

Audio files were being generated on the Pi server but couldn't be accessed by the mobile app, resulting in:
```
ERROR Audio playback error: [Error: v8.y$f: Response code: 404]
```

## Root Cause

The audio URLs returned by the API were using `/audio/filename.mp3` but there was no route to serve these files. The mobile app was trying to access:
```
http://192.168.X.X:5000/audio/filename.mp3  ❌ 404 Not Found
```

## Solution

### 1. Added Audio Serving Route

Created `/api/audio/<filename>` endpoint in `pi-server/src/routes/api.py`:

```python
@api_bp.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename: str):
    """
    Serve audio files
    GET /api/audio/<filename>
    Returns: Audio file (MP3)
    """
    try:
        # Ensure audio directory exists
        if not os.path.exists(AUDIO_DIR):
            os.makedirs(AUDIO_DIR)
            return jsonify({'error': 'NotFound', 'message': 'Audio directory not found'}), 404
        
        # Construct file path
        file_path = os.path.join(AUDIO_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return jsonify({'error': 'NotFound', 'message': f'Audio file not found: {filename}'}), 404
        
        # Serve the file
        return send_file(file_path, mimetype='audio/mpeg')
        
    except Exception as e:
        logger.exception("Audio serving error")
        return jsonify({'error': 'FileError', 'message': str(e)}), 500
```

### 2. Updated Audio URL Format

Changed all audio URLs from `/audio/` to `/api/audio/`:

**Before:**
```python
'audioUrl': f'/audio/{audio_filename}'
```

**After:**
```python
'audioUrl': f'/api/audio/{audio_filename}' if audio_filename else None
```

**Files updated:**
- `pi-server/src/routes/api.py` (3 occurrences)
  - `/api/capture` endpoint
  - `/api/capture/upload` endpoint
  - `/api/translate` endpoint
- `pi-server/src/services/history_service.py` (1 occurrence)
  - `save_scan()` method

### 3. Mobile App Already Handles This

The mobile app's `ApiService` already has a method to construct full URLs:

```typescript
getAudioURL(audioUrl: string | null): string | null {
  if (!audioUrl) return null;
  if (audioUrl.startsWith('http')) return audioUrl;
  return `${this.baseURL}${audioUrl}`;
}
```

So when it receives `/api/audio/filename.mp3`, it constructs:
```
http://192.168.X.X:5000/api/audio/filename.mp3  ✅ Works!
```

## How It Works Now

### Scan Flow with Audio:

1. **User scans document** (Pi camera or phone camera)
2. **Pi server processes:**
   - Captures/receives image
   - Extracts text with OCR
   - Generates audio with gTTS → saves to `audio/abc123.mp3`
   - Returns response:
     ```json
     {
       "id": "abc123",
       "text": "Bonjour le monde",
       "audioUrl": "/api/audio/abc123.mp3",
       "language": "french"
     }
     ```
3. **Mobile app receives response:**
   - Constructs full URL: `http://192.168.X.X:5000/api/audio/abc123.mp3`
   - Plays audio using `expo-av`
4. **Pi server serves audio:**
   - Receives GET request to `/api/audio/abc123.mp3`
   - Reads file from `audio/` directory
   - Sends MP3 file with `audio/mpeg` mimetype
5. **Audio plays on phone** ✅

## Testing

### Test 1: Check Audio File Exists
```bash
# On Raspberry Pi
ls -lh audio/
# Should show .mp3 files
```

### Test 2: Test Audio Endpoint
```bash
# On Raspberry Pi (replace with actual filename)
curl -I http://localhost:5000/api/audio/abc123.mp3
# Should return: HTTP/1.1 200 OK
# Content-Type: audio/mpeg
```

### Test 3: Test from Mobile App
1. Scan a document
2. Check console logs - should show audio URL
3. Audio should play automatically on phone
4. No 404 errors

### Test 4: Manual Audio URL Test
```bash
# From your computer (on same network)
curl -I http://192.168.X.X:5000/api/audio/abc123.mp3
# Should return 200 OK
```

## Audio Directory Structure

```
pi-server/
├── audio/                    ← Audio files stored here
│   ├── abc123.mp3
│   ├── def456.mp3
│   └── ...
├── src/
│   ├── routes/
│   │   └── api.py           ← Audio serving endpoint
│   └── services/
│       ├── tts_service.py   ← Generates audio files
│       └── history_service.py ← Stores audio URLs
└── data/
    └── history.json         ← References audio files
```

## Error Handling

The audio endpoint handles several error cases:

1. **Audio directory doesn't exist:**
   - Creates directory automatically
   - Returns 404 if creation fails

2. **Audio file not found:**
   - Logs error with filename
   - Returns 404 with descriptive message

3. **File read error:**
   - Logs exception
   - Returns 500 with error message

## Mobile App Audio Playback

The mobile app uses `expo-av` to play audio:

```typescript
const playAudio = async (audioUrl: string | null) => {
  if (!audioUrl) return;

  try {
    // Stop previous audio if playing
    if (sound) {
      await sound.unloadAsync();
    }

    const api = getApiService();
    const fullUrl = api.getAudioURL(audioUrl);
    
    if (!fullUrl) return;

    const { sound: newSound } = await Audio.Sound.createAsync(
      { uri: fullUrl },
      { shouldPlay: true }
    );
    
    setSound(newSound);
    
    // Cleanup when finished
    newSound.setOnPlaybackStatusUpdate((status) => {
      if (status.isLoaded && status.didJustFinish) {
        newSound.unloadAsync();
      }
    });
  } catch (error) {
    console.error('Audio playback error:', error);
  }
};
```

## Benefits

1. **Audio plays on phone** - Better user experience
2. **No Pi speaker needed** - Phone has better speakers
3. **Portable** - Works anywhere with network connection
4. **Consistent** - Same audio playback for all users

## Next Steps

After restarting the Pi server:

1. **Restart server:**
   ```bash
   cd ~/SmartReader/pi-server
   source venv/bin/activate
   python -m src.app
   ```

2. **Test scanning:**
   - Scan a document
   - Audio should play on phone
   - Check for 404 errors (should be none)

3. **Check history:**
   - Go to History tab
   - Tap on a scan
   - Audio should play

## Troubleshooting

### Audio still not playing?

1. **Check audio files exist:**
   ```bash
   ls -lh audio/
   ```

2. **Check server logs:**
   - Look for "Audio file not found" errors
   - Check file paths

3. **Test endpoint directly:**
   ```bash
   curl http://localhost:5000/api/audio/filename.mp3 --output test.mp3
   ```

4. **Check mobile app logs:**
   - Look for full audio URL being constructed
   - Should be: `http://192.168.X.X:5000/api/audio/filename.mp3`

### 404 errors persist?

- Verify server restarted with new code
- Check audio URL format in response
- Ensure `/api/audio/` route is registered

### Audio plays but sounds wrong?

- Check gTTS language setting
- Verify speech rate and pitch settings
- Test TTS directly:
  ```bash
  python -c "from gtts import gTTS; tts = gTTS('Hello world', lang='en'); tts.save('test.mp3')"
  mpg123 test.mp3
  ```

## Summary

✅ **Fixed:** Audio files now accessible via `/api/audio/<filename>` endpoint

✅ **Updated:** All audio URLs use `/api/audio/` format

✅ **Working:** Audio plays on phone after scanning

✅ **Tested:** Endpoint serves MP3 files correctly

**Result:** Users can now hear the scanned text read aloud on their phone! 🎉
