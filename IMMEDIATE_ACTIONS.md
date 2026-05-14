# ⚡ IMMEDIATE ACTIONS - Fix Connection Now

## Your Current Situation

**Problem:** Phone and Raspberry Pi are on **different networks** → Can't communicate

**Evidence from your logs:**
```
(2170) accepted ('192.168.137.1', 57514)  ← Pi received connection from 192.168.137.1
192.168.137.1 - - [06/May/2026 21:51:58] "GET /api/health HTTP/1.1" 200
```

This shows:
- Pi is accessible at some IP on `192.168.137.X` network
- Your phone is likely on a different network (e.g., `192.168.1.X`)
- They can't see each other

---

## Fix It Now (3 Steps)

### Step 1: Find Pi's Current IP

```bash
# On Raspberry Pi, run:
hostname -I
```

**Example output:** `192.168.137.123 172.17.0.1`

The first IP is what you need: `192.168.137.123`

### Step 2: Connect Phone to Same Network

**Option A: Connect Phone to Pi's Network**
1. On your phone: Settings → WiFi
2. Look for the network Pi is connected to
3. Connect to that network
4. Your phone will get an IP like `192.168.137.X`

**Option B: Use Phone Hotspot (Easier)**
1. Enable phone hotspot
2. On Pi, connect to phone's hotspot:
   ```bash
   sudo raspi-config
   # → System Options → Wireless LAN
   # Enter your phone's hotspot name and password
   sudo reboot
   ```
3. After reboot, get new IP:
   ```bash
   hostname -I
   ```
4. Pi will get IP like `192.168.43.X`

### Step 3: Update App Settings

1. Open SmartReader app
2. Go to **Settings** tab
3. Tap **"Pi Connection Settings"**
4. Enter Pi's IP (from Step 1)
5. Port: `5000`
6. Tap **"Save & Connect"**

**Result:** Should see 🟢 **Connected**

---

## Verify It's Working

### Test 1: Check Pi's IP and Network
```bash
# On Raspberry Pi
hostname -I
iwgetid -r
```

**Example output:**
```
192.168.137.123
MyWiFiNetwork
```

### Test 2: Check Server is Running
```bash
# On Raspberry Pi
curl http://localhost:5000/api/health
```

**Expected:**
```json
{"status": "ok", "timestamp": "2026-05-07T..."}
```

### Test 3: Check Network Access
```bash
# On Raspberry Pi (replace with your Pi's IP)
curl http://192.168.137.123:5000/api/health
```

**Expected:** Same as Test 2

### Test 4: Check Mobile App
1. Open SmartReader app
2. Top of Home screen should show: 🟢 **Connected**

---

## Quick Diagnostic Script

Run this on your Raspberry Pi:

```bash
cd ~/SmartReader/pi-server
bash network_setup.sh
```

This will show:
- ✅ WiFi connection status
- ✅ IP address to use
- ✅ Server health
- ✅ What to enter in mobile app

---

## Understanding Your Network

### Current Setup (Based on Logs)

Your Pi is on network: `192.168.137.X`

This could be:
- A mobile hotspot
- A specific WiFi network
- A USB tethering connection

**Your phone needs to be on the same `192.168.137.X` network.**

### How to Check Phone's Network

1. Settings → WiFi → Tap connected network
2. Look for IP address
3. Should be `192.168.137.X` (same as Pi)

**If different (e.g., `192.168.1.X`):**
- Phone is on different network
- Won't work until both on same network

---

## Recommended Setup: Phone Hotspot

**Why:** Simplest and most portable

**Steps:**

1. **Enable phone hotspot**
   - Settings → Hotspot & Tethering
   - Turn on WiFi hotspot
   - Note the network name and password

2. **Connect Pi to hotspot**
   ```bash
   sudo raspi-config
   # → System Options → Wireless LAN
   # Enter hotspot name and password
   sudo reboot
   ```

3. **Get Pi's new IP**
   ```bash
   hostname -I
   ```
   Should be like: `192.168.43.100`

4. **Update app**
   - Settings → Pi Connection Settings
   - Enter new IP: `192.168.43.100`
   - Port: `5000`
   - Save & Connect

**Advantages:**
- ✅ Works anywhere
- ✅ No need for WiFi router
- ✅ Pi and phone always on same network

**Disadvantages:**
- ⚠️ Uses phone data (minimal)
- ⚠️ Drains phone battery faster

---

## Alternative: Home WiFi

**Why:** Better for permanent setup

**Steps:**

1. **Connect Pi to home WiFi**
   ```bash
   sudo raspi-config
   # → System Options → Wireless LAN
   # Enter home WiFi name and password
   sudo reboot
   ```

2. **Get Pi's IP**
   ```bash
   hostname -I
   ```
   Should be like: `192.168.1.123`

3. **Connect phone to same WiFi**
   - Settings → WiFi
   - Connect to home WiFi

4. **Update app**
   - Settings → Pi Connection Settings
   - Enter Pi's IP: `192.168.1.123`
   - Port: `5000`
   - Save & Connect

**Advantages:**
- ✅ Stable connection
- ✅ No phone battery drain
- ✅ Faster speeds

**Disadvantages:**
- ⚠️ Only works at home
- ⚠️ Pi's IP may change (use static IP)

---

## Troubleshooting

### "I ran hostname -I but got multiple IPs"

```bash
hostname -I
# Output: 192.168.137.123 172.17.0.1 fe80::1234
```

**Use the first IPv4 address:** `192.168.137.123`

Ignore:
- `172.17.0.1` (Docker)
- `fe80::...` (IPv6)

### "Server not responding"

```bash
# Check if server is running
curl http://localhost:5000/api/health

# If not running, start it
cd ~/SmartReader/pi-server
source venv/bin/activate
python -m src.app
```

### "Connection works then disconnects"

**Cause:** Pi's IP changed (DHCP)

**Fix:** Set static IP
```bash
sudo nano /etc/dhcpcd.conf

# Add at end:
interface wlan0
static ip_address=192.168.137.123/24
static routers=192.168.137.1
static domain_name_servers=8.8.8.8

# Save (Ctrl+X, Y, Enter)
sudo reboot
```

### "Firewall blocking connection"

```bash
# Check firewall
sudo ufw status

# If active, allow port 5000
sudo ufw allow 5000
```

---

## What About the Other Errors?

### ExpoSpeechRecognition Error

**Status:** ✅ **IGNORE THIS**

This is normal in Expo Go. Voice commands are disabled but app works fine without them.

To enable voice commands (optional):
```bash
npx expo run:android
```

### Failed to Download Remote Update

**Status:** ✅ **ALREADY FIXED**

Updated `app.json` to disable updates. If you still see this:
```bash
cd smartreader-mobile-clean
npx expo start --clear
```

---

## Summary Checklist

- [ ] Found Pi's IP address: `hostname -I`
- [ ] Connected phone to same network as Pi
- [ ] Verified both have same IP prefix (e.g., both `192.168.137.X`)
- [ ] Updated app with Pi's IP address
- [ ] Checked connection status: 🟢 Connected
- [ ] Tested scanning with Pi camera
- [ ] Tested scanning with phone camera

---

## Next Steps After Connection

Once you see 🟢 **Connected**:

1. **Test Pi Camera**
   - Tap 📷 **Pi Camera**
   - Should capture and read text

2. **Test Phone Camera**
   - Tap 📱 **Phone Camera**
   - Take photo of text
   - Should process and read

3. **Check History**
   - Go to History tab
   - See past scans

4. **Adjust Settings**
   - Change language
   - Adjust speech rate

---

## Need More Help?

See these guides:
- `START_HERE.md` - Complete setup guide
- `NETWORK_SETUP_GUIDE.md` - Detailed network configuration
- `TROUBLESHOOTING.md` - Common issues and solutions

---

## TL;DR - Just Do This

```bash
# On Raspberry Pi
hostname -I
# Write down the IP (e.g., 192.168.137.123)

# On phone
# 1. Connect to same WiFi as Pi
# 2. Open SmartReader app
# 3. Settings → Pi Connection Settings
# 4. Enter Pi's IP and port 5000
# 5. Save & Connect
# 6. Check for 🟢 Connected
```

**That's it!** 🎉
