# SmartReader Connection Setup - Quick Guide

## 🎯 Goal
Connect your mobile phone to the Raspberry Pi server so they can communicate.

## 📋 Prerequisites
- ✅ Raspberry Pi with SmartReader server installed
- ✅ Mobile phone with SmartReader app installed
- ✅ Both devices on the **same WiFi network**

## 🚀 Quick Setup (3 Steps)

### Step 1: Start the Pi Server

On your Raspberry Pi:

```bash
cd pi-server
python -m src.app
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Running on http://192.168.1.100:5000  ← Note this IP!
```

**Write down the IP address** (e.g., 192.168.1.100)

---

### Step 2: Configure Mobile App

**Option A: Use Default (if mDNS is set up)**
- App will auto-connect to `smartreader.local`
- No configuration needed!
- Skip to Step 3

**Option B: Enter Pi IP Address**

1. Open SmartReader app
2. Go to **Settings** tab (bottom right)
3. Tap **"📡 Pi Connection Settings"** (green button at top)
4. Enter your Pi's IP address (from Step 1)
5. Tap **"Save & Connect"**

---

### Step 3: Verify Connection

1. Go to **Home** tab
2. Look at the status badge at the top
3. Should show **"Connected"** in green ✅

If it shows "Disconnected" in red ❌:
- Tap **"Reconnect"** button
- Check both devices are on same WiFi
- Verify Pi server is running

---

## 🔧 Detailed Setup Options

### Option 1: Using mDNS (Easiest)

**What is it?**
Allows you to use `smartreader.local` instead of IP address.

**Setup on Pi:**
```bash
# Install mDNS service
sudo apt-get update
sudo apt-get install avahi-daemon

# Set hostname
sudo hostnamectl set-hostname smartreader

# Reboot
sudo reboot
```

**Mobile App:**
- No changes needed!
- App uses `smartreader.local` by default

**Test:**
```bash
# From another computer
ping smartreader.local
curl http://smartreader.local:5000/api/health
```

---

### Option 2: Using IP Address (Most Reliable)

**Find Pi IP:**
```bash
hostname -I
# Example output: 192.168.1.100
```

**Configure Mobile App:**
1. Settings → Pi Connection Settings
2. Enter IP: `192.168.1.100`
3. Port: `5000`
4. Save & Connect

**Make IP Static (Optional but Recommended):**
```bash
sudo nano /etc/dhcpcd.conf
```

Add at end:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

Save and reboot.

---

## 🔍 Troubleshooting

### Problem: Can't Connect

**Check 1: Same WiFi Network?**
```bash
# On Pi:
iwgetid -r

# On Phone:
# Settings → WiFi → Check network name
```

**Check 2: Pi Server Running?**
```bash
# Should see Flask server output
python -m src.app
```

**Check 3: Firewall Blocking?**
```bash
# Allow port 5000
sudo ufw allow 5000/tcp
sudo ufw reload
```

**Check 4: Test from Browser**
- On phone, open browser
- Go to: `http://192.168.1.100:5000/api/health`
- Should see: `{"status":"ok",...}`

---

### Problem: "Network Request Failed"

**Solution 1: Check Router AP Isolation**
- Some routers block device-to-device communication
- Access router settings (usually 192.168.1.1)
- Disable "AP Isolation" or "Client Isolation"

**Solution 2: Use Different WiFi**
- Guest networks often block communication
- Use main home network instead

**Solution 3: Restart Everything**
```bash
# Restart Pi
sudo reboot

# Restart mobile app
# Close and reopen
```

---

### Problem: "Connection Timeout"

**Check Network Connectivity:**
```bash
# On Pi, check if online
ping google.com

# Check if WiFi is connected
iwconfig
```

**Check Server Logs:**
- Look at terminal where server is running
- Any error messages?

**Try Different Port:**
- Change port in Pi server
- Update mobile app to match

---

## 📱 Mobile App Connection Settings

### Accessing Settings

1. Open SmartReader app
2. Tap **Settings** tab (bottom navigation)
3. Tap **"📡 Pi Connection Settings"** (green button)

### Configuration Options

**Hostname/IP:**
- `smartreader.local` (if mDNS configured)
- `192.168.1.100` (your Pi's IP)
- `10.0.0.50` (example for different network)

**Port:**
- Default: `5000`
- Change if Pi server uses different port

**Examples:**
- Tap example to auto-fill
- Tap "Reset to Default" to restore defaults

---

## ✅ Connection Checklist

Before asking for help, verify:

- [ ] Pi server is running (`python -m src.app`)
- [ ] Both devices on same WiFi network
- [ ] Pi IP address is correct
- [ ] Port 5000 is not blocked by firewall
- [ ] Can access `http://PI_IP:5000/api/health` from phone browser
- [ ] Router AP Isolation is disabled
- [ ] Mobile app has correct hostname/IP configured

---

## 🎓 Understanding the Connection

```
┌─────────────┐                    ┌──────────────┐
│             │   WiFi Network     │              │
│  Mobile App │ ←─────────────────→│  Pi Server   │
│             │  HTTP REST API     │              │
│  (Phone)    │  Port 5000         │  (Pi 3B)     │
└─────────────┘                    └──────────────┘
```

**What happens:**
1. Mobile app sends HTTP request to Pi
2. Pi processes request (scan, settings, etc.)
3. Pi sends response back to mobile
4. Mobile app displays result

**Requirements:**
- Both on same network
- Pi server listening on port 5000
- No firewall blocking communication
- Correct IP/hostname configured

---

## 🔐 Security Notes

**Current Setup:**
- ⚠️ No authentication
- ⚠️ No encryption (HTTP not HTTPS)
- ⚠️ Local network only

**For Production:**
- Add authentication (JWT tokens)
- Use HTTPS with SSL certificates
- Add rate limiting
- Implement access control

**Current setup is safe for:**
- Home use on private WiFi
- Testing and development
- Trusted local networks

**NOT safe for:**
- Public WiFi
- Internet-exposed servers
- Untrusted networks

---

## 📞 Getting Help

If you're still having issues:

1. **Check Pi Server Logs:**
   - Look at terminal output
   - Any error messages?

2. **Check Mobile App Logs:**
   - Shake device → Debug menu
   - Check console for errors

3. **Test with curl:**
   ```bash
   curl http://PI_IP:5000/api/health
   ```

4. **Verify Network:**
   ```bash
   # Can Pi reach internet?
   ping google.com
   
   # Can phone reach Pi?
   # Use network utility app to ping Pi
   ```

5. **Check Documentation:**
   - `PI_CONNECTION_GUIDE.md` - Detailed guide
   - `QUICK_START.md` - Getting started
   - `IMPLEMENTATION_SUMMARY.md` - System overview

---

## 🎉 Success!

When everything is working:
- ✅ Status badge shows "Connected" (green)
- ✅ Can tap SCAN button
- ✅ History loads
- ✅ Settings can be changed

Now you're ready to use SmartReader! 🚀
