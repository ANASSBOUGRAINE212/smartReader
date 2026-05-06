# SmartReader Deployment Checklist

## 🎯 Quick Deployment Guide

Use this checklist to deploy SmartReader on your Raspberry Pi.

---

## 📦 Before You Start

### Hardware Checklist
- [ ] Raspberry Pi 3B (or newer)
- [ ] MicroSD card (16GB+) with Raspberry Pi OS
- [ ] Logitech C270 webcam
- [ ] Speaker (USB or 3.5mm)
- [ ] Power supply (5V 2.5A)
- [ ] WiFi network access

### Software Checklist
- [ ] Raspberry Pi Imager installed
- [ ] SSH client (Terminal/PuTTY)
- [ ] SmartReader code ready
- [ ] Mobile phone with Expo Go

---

## 🚀 Raspberry Pi Setup (30-60 minutes)

### Phase 1: OS Installation (10 min)
- [ ] Flash Raspberry Pi OS to SD card
- [ ] Configure WiFi and SSH in imager
- [ ] Set hostname to `smartreader`
- [ ] Insert SD card and boot Pi
- [ ] Wait 2-3 minutes for first boot

### Phase 2: System Update (15 min)
```bash
- [ ] SSH to Pi: ssh pi@smartreader.local
- [ ] Run: sudo apt-get update
- [ ] Run: sudo apt-get upgrade -y
- [ ] Find IP: hostname -I
```

### Phase 3: Install Dependencies (20 min)
```bash
- [ ] Install Python: sudo apt-get install python3-pip python3-venv -y
- [ ] Install OpenCV: sudo apt-get install libopencv-dev python3-opencv -y
- [ ] Install Tesseract: sudo apt-get install tesseract-ocr tesseract-ocr-{ara,fra,eng} -y
- [ ] Install FFmpeg: sudo apt-get install ffmpeg -y
- [ ] Install mDNS: sudo apt-get install avahi-daemon -y
- [ ] Install camera tools: sudo apt-get install v4l-utils -y
```

### Phase 4: Transfer Code (5 min)
**Choose one method:**

**Option A: Git**
```bash
- [ ] Install git: sudo apt-get install git -y
- [ ] Clone repo: git clone <URL> ~/SmartReader
```

**Option B: SCP (from your computer)**
```bash
- [ ] Run: scp -r pi-server pi@smartreader.local:~/SmartReader/
```

**Option C: USB**
```bash
- [ ] Copy pi-server folder to USB
- [ ] Insert USB into Pi
- [ ] Copy: cp -r /media/pi/USB/pi-server ~/SmartReader/
```

### Phase 5: Setup Python Environment (20 min)
```bash
- [ ] Navigate: cd ~/SmartReader/pi-server
- [ ] Create venv: python3 -m venv venv
- [ ] Activate: source venv/bin/activate
- [ ] Upgrade pip: pip install --upgrade pip
- [ ] Install packages: pip install -r requirements.txt
```

### Phase 6: Test Hardware (5 min)
```bash
- [ ] Test camera: v4l2-ctl --list-devices
- [ ] Test speaker: speaker-test -t wav -c 2
- [ ] Test Tesseract: tesseract --version
- [ ] Take photo: fswebcam test.jpg
```

### Phase 7: Start Server (2 min)
```bash
- [ ] Activate venv: source venv/bin/activate
- [ ] Start server: python -m src.app
- [ ] Verify output shows: Running on http://0.0.0.0:5000
- [ ] Test health: curl http://localhost:5000/api/health
```

---

## 📱 Mobile App Setup (10 minutes)

### Phase 1: Install App (5 min)
```bash
- [ ] Navigate: cd smartreader-mobile-clean
- [ ] Install: npm install
- [ ] Start: npm start
- [ ] Scan QR code with Expo Go app
```

### Phase 2: Configure Connection (2 min)
- [ ] Open app on phone
- [ ] Go to Settings tab
- [ ] Tap "📡 Pi Connection Settings"
- [ ] Enter Pi IP (from hostname -I)
- [ ] Port: 5000
- [ ] Tap "Save & Connect"

### Phase 3: Verify Connection (1 min)
- [ ] Go to Home tab
- [ ] Check status badge
- [ ] Should show "Connected" (green)
- [ ] If not, tap "Reconnect"

### Phase 4: Test Functionality (2 min)
- [ ] Tap SCAN button
- [ ] Wait for scan to complete
- [ ] Check text appears
- [ ] Go to History tab
- [ ] Verify scan is saved
- [ ] Go to Settings tab
- [ ] Try changing a setting

---

## 🎤 Voice Commands Setup (5 minutes)

### Enable Voice Commands
- [ ] Tap microphone button (bottom right)
- [ ] Allow microphone permission
- [ ] Button turns red when listening
- [ ] Say "Scan" to test
- [ ] Verify scan triggers

### Test Commands
- [ ] Say "Scan" → Should trigger scan
- [ ] Say "Show history" → Should open history
- [ ] Say "Faster" → Should increase speed
- [ ] Say "Stop" → Should stop playback

---

## 🔧 Optional: Autostart (10 minutes)

### Create Systemd Service
```bash
- [ ] Create service: sudo nano /etc/systemd/system/smartreader.service
- [ ] Copy service configuration (see RASPBERRY_PI_SETUP.md)
- [ ] Save and exit
- [ ] Reload: sudo systemctl daemon-reload
- [ ] Enable: sudo systemctl enable smartreader
- [ ] Start: sudo systemctl start smartreader
- [ ] Check: sudo systemctl status smartreader
```

### Test Autostart
```bash
- [ ] Reboot Pi: sudo reboot
- [ ] Wait 2 minutes
- [ ] Test health: curl http://smartreader.local:5000/api/health
- [ ] Should respond with {"status":"ok"}
```

---

## ✅ Final Verification

### System Health
- [ ] Pi boots successfully
- [ ] Server starts automatically (if configured)
- [ ] Camera detected
- [ ] Speaker works
- [ ] Network accessible

### API Endpoints
```bash
- [ ] Health: curl http://smartreader.local:5000/api/health
- [ ] Settings: curl http://smartreader.local:5000/api/settings
- [ ] History: curl http://smartreader.local:5000/api/history
```

### Mobile App
- [ ] App connects to Pi
- [ ] Scan button works
- [ ] History loads
- [ ] Settings can be changed
- [ ] Voice commands work

### End-to-End Test
- [ ] Place document in front of camera
- [ ] Say "Scan" or tap SCAN button
- [ ] Wait for processing
- [ ] Text appears on screen
- [ ] Audio plays (if TTS configured)
- [ ] Scan appears in history
- [ ] Can replay from history

---

## 🐛 Troubleshooting Quick Fixes

### Pi Won't Boot
- [ ] Check power supply (5V 2.5A minimum)
- [ ] Re-flash SD card
- [ ] Try different SD card

### Can't SSH
- [ ] Check Pi is on network: ping smartreader.local
- [ ] Try IP address instead: ssh pi@192.168.1.100
- [ ] Check SSH enabled in Pi config

### Camera Not Working
- [ ] Check USB connection
- [ ] Run: lsusb | grep Logitech
- [ ] Run: v4l2-ctl --list-devices
- [ ] Add user to video group: sudo usermod -a -G video pi

### Server Won't Start
- [ ] Check Python version: python3 --version (need 3.9+)
- [ ] Activate venv: source venv/bin/activate
- [ ] Check port not in use: sudo netstat -tulpn | grep 5000
- [ ] Check logs for errors

### Mobile App Won't Connect
- [ ] Verify both on same WiFi
- [ ] Check Pi IP is correct
- [ ] Test in browser: http://PI_IP:5000/api/health
- [ ] Check firewall: sudo ufw allow 5000/tcp

### Voice Commands Not Working
- [ ] Check microphone permission in phone settings
- [ ] Tap microphone button to activate
- [ ] Speak clearly in quiet environment
- [ ] Check console for errors

---

## 📊 Performance Checklist

### Optimize for Pi 3B
- [ ] Reduce camera resolution to 640x480
- [ ] Use Tesseract only (disable cloud OCR)
- [ ] Increase swap space to 1024MB
- [ ] Close unnecessary services

### Monitor Performance
```bash
- [ ] Check CPU: top
- [ ] Check memory: free -h
- [ ] Check disk: df -h
- [ ] Check temperature: vcgencmd measure_temp
```

---

## 🔐 Security Checklist

### Basic Security
- [ ] Change default password: passwd
- [ ] Update system regularly
- [ ] Enable firewall: sudo ufw enable
- [ ] Use SSH keys instead of password

### Network Security
- [ ] Use WPA2/WPA3 WiFi
- [ ] Don't expose to internet
- [ ] Use static IP
- [ ] Disable unused services

---

## 📝 Maintenance Schedule

### Daily
- [ ] Check server is running
- [ ] Monitor disk space

### Weekly
- [ ] Update system: sudo apt-get update && upgrade
- [ ] Check logs: sudo journalctl -u smartreader
- [ ] Test all features

### Monthly
- [ ] Clean old logs: sudo journalctl --vacuum-time=30d
- [ ] Backup data: tar -czf backup.tar.gz data/ audio/
- [ ] Check for updates

---

## 📞 Support Resources

### Documentation
- [ ] `RASPBERRY_PI_SETUP.md` - Detailed setup guide
- [ ] `QUICK_START.md` - Quick start guide
- [ ] `CONNECTION_SETUP.md` - Connection help
- [ ] `VOICE_COMMANDS_GUIDE.md` - Voice commands
- [ ] `IMPLEMENTATION_SUMMARY.md` - System overview

### Commands Reference
```bash
# Start server
cd ~/SmartReader/pi-server && source venv/bin/activate && python -m src.app

# Check status
sudo systemctl status smartreader

# View logs
sudo journalctl -u smartreader -f

# Restart
sudo systemctl restart smartreader

# Find IP
hostname -I

# Test health
curl http://localhost:5000/api/health
```

---

## 🎉 Deployment Complete!

When all checkboxes are checked:

✅ Raspberry Pi is configured
✅ SmartReader server is running
✅ Mobile app is connected
✅ Voice commands are working
✅ System is production-ready!

**Estimated Total Time:** 1-2 hours

**Next Steps:**
1. Test with real documents
2. Adjust settings for your needs
3. Train users on voice commands
4. Set up regular backups
5. Monitor performance

**Enjoy your SmartReader system! 📖🎤🚀**
