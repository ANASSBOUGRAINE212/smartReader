# SmartReader Troubleshooting Guide

## Current Issues and Solutions

### 1. ❌ ExpoSpeechRecognition Native Module Error

**Error Message:**
```
ERROR [Error: Cannot find native module 'ExpoSpeechRecognition']
```

**Cause:** Voice commands only work with native builds, not Expo Go.

**Solution:** Voice commands are **disabled in Expo Go** to prevent crashes. The app will work fine without them. The voice command button will show but won't be functional.

**To enable voice commands:**
```bash
# Build native app (requires Android Studio or physical device)
npx expo run:android
```

**Current Status:** ✅ App has graceful fallback - works fine without voice commands in Expo Go.

---

### 2. ❌ Network Connection Issues

**Error Message:**
```
ERROR Failed to load history: [AxiosError: Network Error]
ERROR Failed to load settings: [AxiosError: Network Error]
```

**Cause:** Phone and Raspberry Pi are on **different networks**.

**Solution:** Both devices MUST be on the same WiFi network.

#### Step-by-Step Fix:

1. **Check Pi's IP address:**
   ```bash
   # On Raspberry Pi
   hostname -I
   ```
   Example output: `192.168.137.123`

2. **Check phone's network:**
   - Open phone Settings → WiFi
   - Note the network name (SSID)

3. **Connect Pi to same network:**
   ```bash
   # On Raspberry Pi
   sudo raspi-config
   # Navigate to: System Options → Wireless LAN
   # Enter your WiFi SSID and password
   ```

4. **Verify both on same network:**
   ```bash
   # On Raspberry Pi
   ip addr show wlan0
   ```
   Should show IP like `192.168.X.X` (same subnet as phone)

5. **Update mobile app connection:**
   - Open SmartReader app
   - Go to Settings tab
   - Tap "Pi Connection Settings"
   - Enter Pi's IP address (e.g., `192.168.137.123`)
   - Port: `5000`
   - Tap "Save & Connect"

6. **Test connection:**
   ```bash
   # From your computer (on same network)
   curl http://192.168.137.123:5000/api/health
   ```
   Should return: `{"status": "ok", "timestamp": "..."}`

**Current Status:** ⚠️ **ACTION REQUIRED** - Connect both devices to same WiFi network.

---

### 3. ❌ Failed to Download Remote Update

**Error Message:**
```
java.io.IOException: failed to download remote update
```

**Cause:** Expo trying to download updates from server.

**Solution:** Already fixed in `app.json`:
```json
"updates": {
  "enabled": false,
  "checkAutomatically": "never",
  "fallbackToCacheTimeout": 0
}
```

**If error persists:**
```bash
# Clear Expo cache
cd smartreader-mobile-clean
npx expo start --clear
```

**Current Status:** ✅ Should be fixed. If persists, clear cache.

---

### 4. ⚠️ Route Warning

**Warning Message:**
```
WARN Route "./(tabs)/index.tsx" is missing the required default export
```

**Cause:** Expo Router expecting default export.

**Solution:** File already has default export. This is a false warning - ignore it.

**Current Status:** ✅ Ignore - app works correctly.

---

## Quick Diagnostic Checklist

### On Raspberry Pi:

```bash
# 1. Check Pi is running
curl http://localhost:5000/api/health

# 2. Check Pi's IP address
hostname -I

# 3. Check server is accessible from network
# (Replace 192.168.137.123 with your Pi's IP)
curl http://192.168.137.123:5000/api/health

# 4. Check camera is detected
ls -l /dev/video*

# 5. Check server logs
# Look for connection attempts from phone
```

### On Phone:

1. ✅ Connected to same WiFi as Pi?
2. ✅ Entered correct Pi IP in Connection Settings?
3. ✅ Port set to 5000?
4. ✅ Connection status shows "Connected" (green)?

---

## Network Configuration Examples

### Example 1: Home WiFi
```
Pi IP:    192.168.1.100
Phone IP: 192.168.1.50
Network:  HomeWiFi
Status:   ✅ Same network - will work
```

### Example 2: Different Networks (WON'T WORK)
```
Pi IP:    192.168.137.123  (Hotspot)
Phone IP: 192.168.1.50     (Home WiFi)
Status:   ❌ Different networks - won't work
```

### Example 3: Phone Hotspot
```
1. Enable phone hotspot
2. Connect Pi to phone's hotspot
3. Pi will get IP like: 192.168.43.X
4. Phone's hotspot IP: 192.168.43.1
5. In app, enter Pi's IP (192.168.43.X)
Status: ✅ Will work
```

---

## Testing Connection

### Test 1: Pi Server Health
```bash
# On Raspberry Pi
curl http://localhost:5000/api/health
```
Expected: `{"status": "ok", "timestamp": "..."}`

### Test 2: Network Accessibility
```bash
# From another device on same network
curl http://<PI_IP>:5000/api/health
```
Expected: Same response as Test 1

### Test 3: Mobile App Connection
1. Open SmartReader app
2. Check connection status (top of Home screen)
3. Should show: 🟢 Connected

If Test 1 works but Test 2 fails:
- Firewall blocking port 5000
- Pi and device on different networks

If Test 2 works but Test 3 fails:
- Wrong IP entered in app
- App cache issue (restart app)

---

## Common Issues

### "Connection keeps disconnecting"
- **Cause:** Pi's IP changed (DHCP)
- **Solution:** Set static IP on Pi or use mDNS (`smartreader.local`)

### "Camera not working"
- **Cause:** Permission issue
- **Solution:**
  ```bash
  sudo usermod -a -G video $USER
  # Then reboot
  sudo reboot
  ```

### "No text detected"
- **Cause:** Poor image quality or lighting
- **Solution:** Use phone camera instead (better positioning)

### "Audio not playing on phone"
- **Cause:** Audio URL not accessible
- **Solution:** Check Pi server is serving `/audio/` files

---

## Getting Help

If issues persist:

1. **Check Pi server logs** - Look for error messages
2. **Check phone logs** - Use `npx expo start` and watch console
3. **Verify network** - Both devices on same WiFi
4. **Test endpoints** - Use curl to test each API endpoint
5. **Restart services** - Restart Pi server and mobile app

---

## Current Status Summary

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Voice Commands | ⚠️ Disabled in Expo Go | Use `npx expo run:android` to enable |
| Network Connection | ❌ Not working | **Connect both to same WiFi** |
| Remote Updates | ✅ Fixed | None |
| Pi Server | ✅ Running | None |
| Camera | ✅ Working | None |
| OCR | ✅ Working | None |
| TTS | ✅ Working | None |

**NEXT STEP:** Connect phone and Pi to the same WiFi network, then update connection settings in app.
