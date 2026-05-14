# Network Setup Guide - Quick Reference

## 🚨 CRITICAL: Both Devices Must Be On Same Network

Your phone and Raspberry Pi **MUST** be connected to the **same WiFi network** for the app to work.

---

## Quick Setup (5 Minutes)

### Step 1: Connect Pi to WiFi

```bash
# On Raspberry Pi
sudo raspi-config
```

Navigate to:
- **System Options** → **Wireless LAN**
- Enter your WiFi SSID (network name)
- Enter your WiFi password
- Reboot: `sudo reboot`

### Step 2: Get Pi's IP Address

```bash
# On Raspberry Pi (after reboot)
cd ~/SmartReader/pi-server
bash network_setup.sh
```

This will show you:
```
┌─────────────────────────────┐
│ Hostname: 192.168.1.123     │
│ Port:     5000              │
└─────────────────────────────┘
```

**Write down this IP address!**

### Step 3: Connect Phone to Same WiFi

1. Open phone **Settings** → **WiFi**
2. Connect to the **same network** as Pi
3. Verify you're connected

### Step 4: Configure Mobile App

1. Open **SmartReader** app
2. Go to **Settings** tab (bottom right)
3. Tap **"Pi Connection Settings"**
4. Enter:
   - **Hostname:** `192.168.1.123` (your Pi's IP)
   - **Port:** `5000`
5. Tap **"Save & Connect"**

### Step 5: Verify Connection

You should see:
- 🟢 **Connected** (green dot at top of Home screen)

If you see 🔴 **Disconnected**:
- Check both devices are on same WiFi
- Verify IP address is correct
- Run `bash network_setup.sh` on Pi again

---

## Network Configuration Options

### Option 1: Home WiFi (Recommended)
```
✅ Best for: Home use, stable connection
📡 Setup: Connect both Pi and phone to home WiFi
🔒 Security: Protected by WiFi password
```

### Option 2: Phone Hotspot
```
✅ Best for: Portable use, no WiFi available
📡 Setup: 
   1. Enable phone hotspot
   2. Connect Pi to phone's hotspot
   3. Pi gets IP like 192.168.43.X
   4. Use that IP in app
⚠️  Note: Uses phone data, may be slower
```

### Option 3: Dedicated Router
```
✅ Best for: Permanent installation
📡 Setup: Connect both to dedicated router
🔒 Security: Isolated network
```

---

## Troubleshooting

### Problem: "Connection keeps disconnecting"

**Cause:** Pi's IP address changed (DHCP)

**Solution:** Set static IP on Pi

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface wlan0
static ip_address=192.168.1.123/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save and reboot
sudo reboot
```

### Problem: "Network Error" in app

**Cause:** Phone and Pi on different networks

**Check:**
```bash
# On Pi
hostname -I
# Example: 192.168.1.123

# On phone
# Settings → WiFi → Tap connected network
# Look for IP address
# Example: 192.168.1.50

# First 3 numbers should match!
# ✅ 192.168.1.X - Same network
# ❌ 192.168.137.X vs 192.168.1.X - Different networks
```

### Problem: "Server not responding"

**Check server is running:**
```bash
# On Pi
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{"status": "ok", "timestamp": "2026-05-07T..."}
```

**If not running:**
```bash
cd ~/SmartReader/pi-server
source venv/bin/activate
python -m src.app
```

### Problem: "Port 5000 blocked"

**Check firewall:**
```bash
sudo ufw status
```

**If active, allow port 5000:**
```bash
sudo ufw allow 5000
```

---

## Testing Connection

### Test 1: Pi Server (Local)
```bash
# On Raspberry Pi
curl http://localhost:5000/api/health
```
✅ Should return: `{"status": "ok", ...}`

### Test 2: Pi Server (Network)
```bash
# From your computer (on same network)
curl http://192.168.1.123:5000/api/health
```
✅ Should return same as Test 1

### Test 3: Mobile App
1. Open SmartReader app
2. Check top of Home screen
3. ✅ Should show: 🟢 **Connected**

**If Test 1 works but Test 2 fails:**
- Firewall blocking port 5000
- Pi and computer on different networks

**If Test 2 works but Test 3 fails:**
- Wrong IP in app settings
- Phone on different network
- App cache issue (restart app)

---

## Network Diagnostic Commands

### On Raspberry Pi:

```bash
# Check WiFi connection
iwgetid -r

# Check IP address
hostname -I

# Check server is running
curl http://localhost:5000/api/health

# Check port is open
netstat -tuln | grep 5000

# Check network interfaces
ip addr show

# Ping phone (if you know phone's IP)
ping 192.168.1.50

# Run full diagnostic
bash network_setup.sh
```

### On Phone:

1. Settings → WiFi → Tap connected network
2. Note IP address (e.g., 192.168.1.50)
3. Verify first 3 numbers match Pi's IP

---

## Quick Reference Card

Print this and keep it handy:

```
╔════════════════════════════════════════╗
║   SmartReader Network Quick Setup      ║
╠════════════════════════════════════════╣
║                                        ║
║  1. Connect Pi to WiFi                 ║
║     sudo raspi-config → Wireless LAN   ║
║                                        ║
║  2. Get Pi IP                          ║
║     bash network_setup.sh              ║
║                                        ║
║  3. Connect phone to SAME WiFi         ║
║                                        ║
║  4. In app: Settings → Pi Connection   ║
║     Enter Pi IP and port 5000          ║
║                                        ║
║  5. Check: 🟢 Connected                ║
║                                        ║
╠════════════════════════════════════════╣
║  Troubleshooting:                      ║
║  • Both on same WiFi? Check SSID       ║
║  • Server running? curl localhost:5000 ║
║  • Firewall? sudo ufw allow 5000       ║
╚════════════════════════════════════════╝
```

---

## Common Network Patterns

### Pattern 1: Same Subnet ✅
```
Pi:    192.168.1.123
Phone: 192.168.1.50
Router: 192.168.1.1
Status: WILL WORK
```

### Pattern 2: Different Subnets ❌
```
Pi:    192.168.137.123  (Hotspot)
Phone: 192.168.1.50     (Home WiFi)
Status: WON'T WORK
```

### Pattern 3: Phone Hotspot ✅
```
Phone Hotspot: 192.168.43.1
Pi:           192.168.43.100
Status: WILL WORK
```

---

## Next Steps After Connection

Once connected (🟢 **Connected**):

1. **Test Pi Camera:**
   - Tap 📷 **Pi Camera** button
   - Should capture and process text

2. **Test Phone Camera:**
   - Tap 📱 **Phone Camera** button
   - Take photo of text
   - Should process on Pi

3. **Check Audio:**
   - After scan, audio should play on phone
   - Text should be read aloud

4. **View History:**
   - Go to **History** tab
   - See past scans

5. **Adjust Settings:**
   - Go to **Settings** tab
   - Change language, speech rate, etc.

---

## Support

If you're still having issues:

1. Run `bash network_setup.sh` on Pi
2. Check all items are ✅
3. Verify phone and Pi on same WiFi
4. Restart both Pi server and mobile app
5. Check `TROUBLESHOOTING.md` for more help
