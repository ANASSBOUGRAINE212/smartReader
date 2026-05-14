# 🚀 START HERE - SmartReader Setup

## Current Status

You're seeing these errors because **your phone and Raspberry Pi are on different networks**.

### Errors You're Seeing:
1. ❌ `Network Error` - Can't connect to Pi
2. ❌ `Failed to load history` - Can't reach Pi server
3. ❌ `Failed to load settings` - Can't reach Pi server
4. ⚠️ `ExpoSpeechRecognition` - Voice commands disabled in Expo Go (this is normal)

### The Fix: Connect Both Devices to Same WiFi

---

## 5-Minute Setup

### 1️⃣ On Raspberry Pi

```bash
# Connect to WiFi
sudo raspi-config
# → System Options → Wireless LAN
# Enter your WiFi name and password
# Reboot

# After reboot, get IP address
cd ~/SmartReader/pi-server
bash network_setup.sh
```

**Write down the IP address shown!** Example: `192.168.1.123`

### 2️⃣ On Your Phone

1. **Settings** → **WiFi**
2. Connect to the **SAME WiFi** as Pi
3. Open **SmartReader** app
4. Go to **Settings** tab
5. Tap **"Pi Connection Settings"**
6. Enter Pi's IP address (e.g., `192.168.1.123`)
7. Port: `5000`
8. Tap **"Save & Connect"**

### 3️⃣ Verify

- Top of Home screen should show: 🟢 **Connected**
- If still 🔴 **Disconnected**, see troubleshooting below

---

## Understanding the Errors

### Error: "Cannot find native module 'ExpoSpeechRecognition'"

**This is NORMAL and EXPECTED in Expo Go.**

- Voice commands only work with native builds (`npx expo run:android`)
- The app has graceful fallback - it works fine without voice commands
- You can ignore this error

**To enable voice commands later:**
```bash
npx expo run:android
```

### Error: "Network Error" / "Failed to load history/settings"

**This means phone can't reach Pi server.**

**Causes:**
1. Phone and Pi on different WiFi networks ← **Most common**
2. Pi server not running
3. Wrong IP address in app
4. Firewall blocking port 5000

**Fix:**
1. Verify both on same WiFi
2. Check Pi server is running: `curl http://localhost:5000/api/health`
3. Update IP in app settings
4. Allow port 5000: `sudo ufw allow 5000`

### Error: "failed to download remote update"

**Already fixed in app.json.**

If you still see this:
```bash
cd smartreader-mobile-clean
npx expo start --clear
```

---

## Network Configuration

### ✅ Correct Setup (Same Network)
```
Pi:    192.168.1.123    WiFi: "HomeNetwork"
Phone: 192.168.1.50     WiFi: "HomeNetwork"
Status: WILL WORK ✅
```

### ❌ Incorrect Setup (Different Networks)
```
Pi:    192.168.137.123  WiFi: "Hotspot"
Phone: 192.168.1.50     WiFi: "HomeNetwork"
Status: WON'T WORK ❌
```

**Key Point:** First 3 numbers of IP should match (e.g., both `192.168.1.X`)

---

## Quick Diagnostic

### On Raspberry Pi:

```bash
# 1. Check WiFi
iwgetid -r
# Should show your WiFi name

# 2. Check IP
hostname -I
# Should show IP like 192.168.X.X

# 3. Check server
curl http://localhost:5000/api/health
# Should return: {"status": "ok", ...}

# 4. Run full diagnostic
bash network_setup.sh
```

### On Phone:

1. Settings → WiFi → Check connected network
2. Should be same as Pi's WiFi
3. Note your phone's IP address
4. First 3 numbers should match Pi's IP

---

## Testing the Connection

### Test 1: Pi Server Running?
```bash
# On Pi
curl http://localhost:5000/api/health
```
✅ Expected: `{"status": "ok", "timestamp": "..."}`

### Test 2: Network Accessible?
```bash
# From your computer (on same network as Pi)
curl http://192.168.1.123:5000/api/health
```
✅ Expected: Same as Test 1

### Test 3: Mobile App Connected?
1. Open SmartReader app
2. Check top of Home screen
3. ✅ Expected: 🟢 **Connected**

**If Test 1 works but Test 2 fails:**
- Firewall issue: `sudo ufw allow 5000`
- Different networks

**If Test 2 works but Test 3 fails:**
- Wrong IP in app
- Phone on different network
- Restart app

---

## Common Issues

### "I don't know my Pi's IP address"

```bash
# On Raspberry Pi
hostname -I
```

Or use the network setup script:
```bash
cd ~/SmartReader/pi-server
bash network_setup.sh
```

### "Pi's IP keeps changing"

Set a static IP:
```bash
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface wlan0
static ip_address=192.168.1.123/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8

# Save and reboot
sudo reboot
```

### "Can't connect Pi to WiFi"

```bash
# Method 1: raspi-config
sudo raspi-config
# → System Options → Wireless LAN

# Method 2: Manual
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add:
network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
}

# Restart WiFi
sudo systemctl restart dhcpcd
```

### "Server not starting"

```bash
cd ~/SmartReader/pi-server
source venv/bin/activate

# Check for errors
python -m src.app

# If port already in use:
sudo lsof -i :5000
# Kill the process and restart
```

---

## What Should Work Now

Once connected (🟢 **Connected**):

### ✅ Pi Camera Scan
1. Tap 📷 **Pi Camera** button
2. Pi captures image
3. Text extracted and displayed
4. Audio plays on phone

### ✅ Phone Camera Scan
1. Tap 📱 **Phone Camera** button
2. Take photo with phone
3. Image uploaded to Pi
4. Text extracted and displayed
5. Audio plays on phone

### ✅ History
1. Go to **History** tab
2. See all past scans
3. Tap to view details
4. Swipe to delete

### ✅ Settings
1. Go to **Settings** tab
2. Change language (French/English)
3. Adjust speech rate
4. Configure Pi connection

### ⚠️ Voice Commands
- **Disabled in Expo Go** (this is normal)
- To enable: `npx expo run:android`
- App works fine without them

---

## Next Steps

1. **Fix Network Connection** (most important!)
   - Connect both to same WiFi
   - Update IP in app settings
   - Verify 🟢 Connected

2. **Test Scanning**
   - Try Pi camera
   - Try phone camera
   - Check audio playback

3. **Explore Features**
   - View history
   - Adjust settings
   - Test different languages

4. **Optional: Enable Voice Commands**
   - Build native app: `npx expo run:android`
   - Requires Android Studio or physical device

---

## Getting Help

If you're still stuck:

1. **Run diagnostics:**
   ```bash
   # On Pi
   bash network_setup.sh
   ```

2. **Check detailed guides:**
   - `NETWORK_SETUP_GUIDE.md` - Network configuration
   - `TROUBLESHOOTING.md` - Common issues
   - `CONNECTION_SETUP.md` - Connection details

3. **Verify basics:**
   - [ ] Pi connected to WiFi
   - [ ] Phone connected to same WiFi
   - [ ] Pi server running
   - [ ] Correct IP in app
   - [ ] Port 5000 allowed

---

## Summary

**Your main issue:** Phone and Pi are on different networks.

**The fix:**
1. Connect Pi to WiFi: `sudo raspi-config`
2. Get Pi's IP: `bash network_setup.sh`
3. Connect phone to same WiFi
4. Enter Pi's IP in app settings
5. Verify: 🟢 Connected

**Voice commands:** Disabled in Expo Go (this is normal, app works fine without them)

**Once connected:** Everything should work - scanning, history, settings, audio playback

---

## Quick Command Reference

```bash
# On Raspberry Pi

# Connect to WiFi
sudo raspi-config

# Get IP address
hostname -I

# Run diagnostics
cd ~/SmartReader/pi-server
bash network_setup.sh

# Start server
cd ~/SmartReader/pi-server
source venv/bin/activate
python -m src.app

# Check server health
curl http://localhost:5000/api/health

# Allow firewall
sudo ufw allow 5000
```

---

**Ready?** Start with Step 1: Connect Pi to WiFi! 🚀
